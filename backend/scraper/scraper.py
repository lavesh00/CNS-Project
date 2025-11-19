"""
Web Scraper
Playwright-based web scraping with asset downloading
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
import json

import structlog
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
import httpx

logger = structlog.get_logger()


class WebScraper:
    """Scrapes websites with Playwright"""
    
    def __init__(self,
                 output_dir: Optional[Path] = None,
                 max_depth: int = 2,
                 respect_robots: bool = True):
        """Initialize scraper
        
        Args:
            output_dir: Directory to save scraped content
            max_depth: Maximum crawl depth
            respect_robots: Respect robots.txt
        """
        if output_dir is None:
            output_dir = Path("scraped")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_depth = max_depth
        self.respect_robots = respect_robots
        
        self.visited_urls: Set[str] = set()
        self.scraped_pages: List[Dict] = []
        self.assets: Dict[str, str] = {}  # URL -> local path
        
        self.browser: Optional[Browser] = None
        self.stop_requested = False
        
        logger.info("Web scraper initialized",
                   output_dir=str(self.output_dir),
                   max_depth=max_depth)
    
    async def scrape(self, url: str, allowed_domains: Optional[List[str]] = None) -> Dict:
        """Scrape a website
        
        Args:
            url: Starting URL
            allowed_domains: List of allowed domains (defaults to same domain)
        
        Returns:
            Scraping summary
        """
        logger.info("Starting scrape", url=url)
        
        # Parse starting URL
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc
        
        if allowed_domains is None:
            allowed_domains = [base_domain]
        
        # Start Playwright
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=True)
            
            try:
                # Scrape recursively
                await self._scrape_recursive(url, 0, allowed_domains)
                
                # Save manifest
                await self._save_manifest()
                
                logger.info("Scraping complete",
                           pages=len(self.scraped_pages),
                           assets=len(self.assets))
                
                return {
                    "success": True,
                    "pages_scraped": len(self.scraped_pages),
                    "assets_downloaded": len(self.assets),
                    "output_dir": str(self.output_dir)
                }
                
            finally:
                await self.browser.close()
                self.browser = None
    
    async def _scrape_recursive(self,
                                url: str,
                                depth: int,
                                allowed_domains: List[str]):
        """Recursively scrape pages"""
        
        # Check stop conditions
        if self.stop_requested:
            return
        
        if depth > self.max_depth:
            return
        
        if url in self.visited_urls:
            return
        
        # Check domain
        parsed_url = urlparse(url)
        if not any(domain in parsed_url.netloc for domain in allowed_domains):
            return
        
        self.visited_urls.add(url)
        
        logger.debug("Scraping page", url=url, depth=depth)
        
        try:
            # Create new page
            page = await self.browser.new_page()
            
            # Navigate to URL
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Get page content
            html_content = await page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Save page
            page_data = {
                "url": url,
                "depth": depth,
                "title": soup.title.string if soup.title else "",
                "local_path": await self._save_page(url, html_content, soup)
            }
            
            self.scraped_pages.append(page_data)
            
            # Download assets
            await self._download_assets(url, soup)
            
            # Find links
            links = await self._extract_links(url, soup)
            
            await page.close()
            
            # Recursively scrape links
            for link in links[:10]:  # Limit links per page
                await self._scrape_recursive(link, depth + 1, allowed_domains)
            
        except Exception as e:
            logger.error("Failed to scrape page", url=url, error=str(e))
    
    async def _save_page(self, url: str, html_content: str, soup: BeautifulSoup) -> str:
        """Save page HTML"""
        
        # Generate filename from URL
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/")
        
        if not path or path.endswith("/"):
            path += "index.html"
        elif not path.endswith(".html"):
            path += ".html"
        
        # Create directories
        page_path = self.output_dir / "pages" / path
        page_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rewrite asset URLs in HTML
        html_rewritten = self._rewrite_urls(html_content, url)
        
        # Save HTML
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(html_rewritten)
        
        logger.debug("Page saved", path=str(page_path))
        
        return str(page_path.relative_to(self.output_dir))
    
    def _rewrite_urls(self, html: str, base_url: str) -> str:
        """Rewrite URLs to use local paths"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Rewrite image sources
        for img in soup.find_all('img'):
            if img.get('src'):
                absolute_url = urljoin(base_url, img['src'])
                if absolute_url in self.assets:
                    img['src'] = f"../../{self.assets[absolute_url]}"
        
        # Rewrite stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                absolute_url = urljoin(base_url, link['href'])
                if absolute_url in self.assets:
                    link['href'] = f"../../{self.assets[absolute_url]}"
        
        # Rewrite scripts
        for script in soup.find_all('script'):
            if script.get('src'):
                absolute_url = urljoin(base_url, script['src'])
                if absolute_url in self.assets:
                    script['src'] = f"../../{self.assets[absolute_url]}"
        
        return str(soup)
    
    async def _download_assets(self, base_url: str, soup: BeautifulSoup):
        """Download page assets (images, CSS, JS)"""
        
        assets_to_download = []
        
        # Images
        for img in soup.find_all('img'):
            if img.get('src'):
                assets_to_download.append(urljoin(base_url, img['src']))
        
        # Stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                assets_to_download.append(urljoin(base_url, link['href']))
        
        # Scripts
        for script in soup.find_all('script'):
            if script.get('src'):
                assets_to_download.append(urljoin(base_url, script['src']))
        
        # Download each asset
        for asset_url in assets_to_download:
            if asset_url not in self.assets:
                local_path = await self._download_asset(asset_url)
                if local_path:
                    self.assets[asset_url] = local_path
    
    async def _download_asset(self, url: str) -> Optional[str]:
        """Download a single asset"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                
                # Determine file path
                parsed_url = urlparse(url)
                path = parsed_url.path.lstrip("/")
                
                if not path:
                    path = "index"
                
                # Save asset
                asset_path = self.output_dir / "assets" / path
                asset_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(asset_path, 'wb') as f:
                    f.write(response.content)
                
                logger.debug("Asset downloaded", url=url)
                
                return str(asset_path.relative_to(self.output_dir))
                
        except Exception as e:
            logger.warning("Failed to download asset", url=url, error=str(e))
            return None
    
    async def _extract_links(self, base_url: str, soup: BeautifulSoup) -> List[str]:
        """Extract links from page"""
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # Make absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Filter out anchors, mailto, etc.
            if absolute_url.startswith('http'):
                links.append(absolute_url)
        
        return links
    
    async def _save_manifest(self):
        """Save scraping manifest"""
        manifest = {
            "pages": self.scraped_pages,
            "total_pages": len(self.scraped_pages),
            "total_assets": len(self.assets),
            "max_depth": self.max_depth
        }
        
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info("Manifest saved", path=str(manifest_path))
    
    def stop(self):
        """Request stop"""
        logger.info("Stop requested for scraper")
        self.stop_requested = True

