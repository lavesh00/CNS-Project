import { useState, useEffect, useCallback } from 'react'
import HeroBanner from '../components/HeroBanner'
import GenreFilter from '../components/GenreFilter'
import ContentRow from '../components/ContentRow'
import MediaGrid from '../components/MediaGrid'
import useInfiniteScroll from '../hooks/useInfiniteScroll'
import { getPopularMovies, discoverMovies, getTopRatedMovies, getActionMovies } from '../services/tmdb'
import { MOVIE_GENRES } from '../utils/constants'

export default function Movies() {
  const [selectedGenre, setSelectedGenre] = useState(null)
  const [heroItems, setHeroItems] = useState([])

  useEffect(() => {
    getPopularMovies()
      .then((res) => {
        const results = (res.data.results || []).filter(m => m.backdrop_path)
        setHeroItems(results.slice(0, 5))
      })
      .catch(() => {})
  }, [])

  const fetcher = useCallback(
    (page) => selectedGenre ? discoverMovies(selectedGenre, page) : getPopularMovies(page),
    [selectedGenre]
  )
  const { results, loading, sentinelRef, reset } = useInfiniteScroll(fetcher)
  useEffect(() => { reset() }, [selectedGenre, reset])

  return (
    <div>
      {/* Mini hero — no autorotate for category pages */}
      {heroItems.length > 0 && <HeroBanner items={heroItems.slice(0, 3)} />}

      <div className={`${heroItems.length > 0 ? '-mt-10 sm:-mt-14' : 'pt-[68px]'} relative z-10 pb-8`}>
        <div className="px-3 sm:px-6 md:px-12 pt-4 pb-2 flex items-center gap-3">
          <h1 className="text-2xl md:text-3xl font-black">Movies</h1>
        </div>
        <GenreFilter
          genres={MOVIE_GENRES}
          selectedGenre={selectedGenre}
          onSelect={setSelectedGenre}
        />
        {!selectedGenre && (
          <>
            <ContentRow title="Top Rated" fetcher={getTopRatedMovies} mediaType="movie" />
            <ContentRow title="Action" fetcher={getActionMovies} mediaType="movie" />
          </>
        )}
        <MediaGrid items={results} loading={loading} sentinelRef={sentinelRef} mediaType="movie" />
      </div>
    </div>
  )
}
