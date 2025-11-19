"""
Reasoning Summarizer
Two-stage summarization: Extractive (TextRank) + Structured reasoning
"""

import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

import structlog
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from models.runtime import LlamaCppRuntime, GenerationConfig

logger = structlog.get_logger()


@dataclass
class Claim:
    """A claim with evidence"""
    statement: str
    evidence: List[str]  # file:line references
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Summary:
    """Structured summary"""
    progress_overview: str
    completed_todos: List[str]
    claims: List[Claim]
    open_issues: List[str]
    next_suggestions: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "progress_overview": self.progress_overview,
            "completed_todos": self.completed_todos,
            "claims": [c.to_dict() for c in self.claims],
            "open_issues": self.open_issues,
            "next_suggestions": self.next_suggestions
        }


class Summarizer:
    """Creates compact summaries of agent progress"""
    
    SUMMARIZER_SYSTEM_PROMPT = """You are an expert at creating concise, evidence-backed summaries of software development progress.

You will receive key extracted sentences from logs, code changes, and execution history.

Create a structured summary in JSON format:

{
  "progress_overview": "Brief paragraph summarizing what has been accomplished",
  "completed_todos": ["list", "of", "completed", "tasks"],
  "claims": [
    {
      "statement": "Specific claim about what was done",
      "evidence": ["file.py:10", "file.py:25"]
    }
  ],
  "open_issues": ["list", "of", "outstanding", "problems"],
  "next_suggestions": ["suggested", "next", "steps"]
}

Rules:
1. Be concise and specific
2. Always include file:line evidence for claims
3. Focus on facts, not speculation
4. Highlight blockers and failures
5. Output ONLY JSON
"""
    
    def __init__(self, runtime: Optional[LlamaCppRuntime] = None):
        """Initialize summarizer"""
        self.runtime = runtime
        self.stemmer = Stemmer("english")
        
        logger.info("Summarizer initialized")
    
    async def summarize(self,
                       logs: List[str],
                       work_results: List[Dict],
                       code_changes: List[Dict]) -> Summary:
        """Create summary from logs, results, and changes
        
        Args:
            logs: Log messages
            work_results: Worker execution results
            code_changes: Code changes made
        
        Returns:
            Structured Summary
        """
        logger.info("Creating summary",
                   logs=len(logs),
                   results=len(work_results),
                   changes=len(code_changes))
        
        # Stage 1: Extractive summarization with TextRank
        extracted = self._extract_key_sentences(logs, work_results, code_changes)
        
        logger.debug("Extracted key sentences", count=len(extracted))
        
        # Stage 2: Structured reasoning with LLM
        if self.runtime and extracted:
            summary = await self._structured_summary(extracted)
        else:
            summary = self._create_basic_summary(work_results, code_changes)
        
        logger.info("Summary created")
        
        return summary
    
    def _extract_key_sentences(self,
                               logs: List[str],
                               work_results: List[Dict],
                               code_changes: List[Dict]) -> List[str]:
        """Extract key sentences using TextRank"""
        
        # Combine all text sources
        text_parts = []
        
        # Add logs
        text_parts.extend(logs)
        
        # Add work result explanations
        for result in work_results:
            if result.get("explanation"):
                text_parts.append(result["explanation"])
            
            # Add file changes as sentences
            for patch in result.get("patches", []):
                file = patch.get("file", "")
                action = patch.get("action", "")
                text_parts.append(f"File {file} was {action}ed")
        
        # Add code change descriptions
        for change in code_changes:
            if change.get("description"):
                text_parts.append(change["description"])
        
        if not text_parts:
            return []
        
        # Combine into single text
        full_text = "\n".join(text_parts)
        
        # Use TextRank to extract key sentences
        try:
            parser = PlaintextParser.from_string(full_text, Tokenizer("english"))
            summarizer = TextRankSummarizer(self.stemmer)
            summarizer.stop_words = get_stop_words("english")
            
            # Get top sentences
            summary_sentences = summarizer(parser.document, sentences_count=10)
            
            extracted = [str(sentence) for sentence in summary_sentences]
            
            return extracted
            
        except Exception as e:
            logger.error("TextRank extraction failed", error=str(e))
            # Fallback: return recent logs
            return text_parts[-10:]
    
    async def _structured_summary(self, extracted_sentences: List[str]) -> Summary:
        """Create structured summary using LLM"""
        
        # Build prompt
        prompt = f"{self.SUMMARIZER_SYSTEM_PROMPT}\n\n## Key Information\n\n"
        prompt += "\n".join(f"- {sentence}" for sentence in extracted_sentences)
        prompt += "\n\n## Generate Summary JSON:"
        
        try:
            summary_json = await self.runtime.generate_json(
                prompt,
                config=GenerationConfig(
                    temperature=0.3,
                    max_tokens=1024,
                    json_mode=True
                )
            )
            
            return self._parse_summary(summary_json)
            
        except Exception as e:
            logger.error("Failed to generate structured summary", error=str(e))
            # Fallback
            return Summary(
                progress_overview=" ".join(extracted_sentences[:3]),
                completed_todos=[],
                claims=[],
                open_issues=[],
                next_suggestions=[]
            )
    
    def _parse_summary(self, summary_json: Dict) -> Summary:
        """Parse summary JSON into Summary object"""
        try:
            # Parse claims
            claims = []
            for claim_data in summary_json.get("claims", []):
                claim = Claim(
                    statement=claim_data.get("statement", ""),
                    evidence=claim_data.get("evidence", [])
                )
                claims.append(claim)
            
            summary = Summary(
                progress_overview=summary_json.get("progress_overview", ""),
                completed_todos=summary_json.get("completed_todos", []),
                claims=claims,
                open_issues=summary_json.get("open_issues", []),
                next_suggestions=summary_json.get("next_suggestions", [])
            )
            
            return summary
            
        except Exception as e:
            logger.error("Failed to parse summary", error=str(e))
            return Summary(
                progress_overview="Summary parsing failed",
                completed_todos=[],
                claims=[],
                open_issues=["Failed to create summary"],
                next_suggestions=[]
            )
    
    def _create_basic_summary(self,
                             work_results: List[Dict],
                             code_changes: List[Dict]) -> Summary:
        """Create basic summary without LLM"""
        completed = []
        issues = []
        files_changed = set()
        
        for result in work_results:
            if result.get("status") == "done":
                completed.append(result.get("explanation", "Task completed"))
            elif result.get("status") == "cannot":
                issues.append(result.get("explanation", "Task failed"))
            
            for patch in result.get("patches", []):
                files_changed.add(patch.get("file", ""))
        
        overview = f"Completed {len(completed)} tasks. Modified {len(files_changed)} files."
        
        return Summary(
            progress_overview=overview,
            completed_todos=completed,
            claims=[],
            open_issues=issues,
            next_suggestions=[]
        )

