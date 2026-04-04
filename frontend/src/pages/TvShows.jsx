import { useState, useEffect, useCallback } from 'react'
import HeroBanner from '../components/HeroBanner'
import GenreFilter from '../components/GenreFilter'
import ContentRow from '../components/ContentRow'
import MediaGrid from '../components/MediaGrid'
import useInfiniteScroll from '../hooks/useInfiniteScroll'
import { getPopularTv, discoverTv, getTopRatedTv } from '../services/tmdb'
import { TV_GENRES } from '../utils/constants'

export default function TvShows() {
  const [selectedGenre, setSelectedGenre] = useState(null)
  const [heroItems, setHeroItems] = useState([])

  useEffect(() => {
    getPopularTv()
      .then((res) => {
        const results = (res.data.results || []).filter(m => m.backdrop_path)
        setHeroItems(results.slice(0, 3))
      })
      .catch(() => {})
  }, [])

  const fetcher = useCallback(
    (page) => selectedGenre ? discoverTv(selectedGenre, page) : getPopularTv(page),
    [selectedGenre]
  )
  const { results, loading, sentinelRef, reset } = useInfiniteScroll(fetcher)
  useEffect(() => { reset() }, [selectedGenre, reset])

  return (
    <div>
      {heroItems.length > 0 && <HeroBanner items={heroItems} />}
      <div className={`${heroItems.length > 0 ? '-mt-10 sm:-mt-14' : 'pt-[68px]'} relative z-10 pb-8`}>
        <div className="px-3 sm:px-6 md:px-12 pt-4 pb-2">
          <h1 className="text-2xl md:text-3xl font-black">TV Shows</h1>
        </div>
        <GenreFilter genres={TV_GENRES} selectedGenre={selectedGenre} onSelect={setSelectedGenre} />
        {!selectedGenre && (
          <ContentRow title="Top Rated TV" fetcher={getTopRatedTv} mediaType="tv" />
        )}
        <MediaGrid items={results} loading={loading} sentinelRef={sentinelRef} mediaType="tv" />
      </div>
    </div>
  )
}
