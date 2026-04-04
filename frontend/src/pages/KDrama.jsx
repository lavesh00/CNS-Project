import { useState, useEffect, useCallback } from 'react'
import HeroBanner from '../components/HeroBanner'
import ContentRow from '../components/ContentRow'
import MediaGrid from '../components/MediaGrid'
import useInfiniteScroll from '../hooks/useInfiniteScroll'
import { getKDrama } from '../services/tmdb'

export default function KDrama() {
  const [heroItems, setHeroItems] = useState([])

  useEffect(() => {
    getKDrama()
      .then((res) => {
        const results = (res.data.results || []).filter(m => m.backdrop_path)
        setHeroItems(results.slice(0, 3))
      })
      .catch(() => {})
  }, [])

  const fetcher = useCallback((page) => getKDrama(page), [])
  const { results, loading, sentinelRef, reset } = useInfiniteScroll(fetcher)

  return (
    <div>
      {heroItems.length > 0 && <HeroBanner items={heroItems} />}
      <div className={`${heroItems.length > 0 ? '-mt-10 sm:-mt-14' : 'pt-[68px]'} relative z-10 pb-8`}>
        <div className="px-3 sm:px-6 md:px-12 pt-4 pb-2">
          <h1 className="text-2xl md:text-3xl font-black">K-Drama</h1>
        </div>
        <ContentRow title="Popular K-Drama" fetcher={getKDrama} mediaType="tv" />
        <MediaGrid items={results} loading={loading} sentinelRef={sentinelRef} mediaType="tv" />
      </div>
    </div>
  )
}
