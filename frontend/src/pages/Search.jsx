import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import MediaGrid from '../components/MediaGrid'
import useDebounce from '../hooks/useDebounce'
import useInfiniteScroll from '../hooks/useInfiniteScroll'
import { searchMulti, getTrending } from '../services/tmdb'
import MediaCard from '../components/MediaCard'

const TRENDING_SEARCHES = ['Marvel', 'DC', 'Star Wars', 'Game of Thrones', 'Breaking Bad', 'Stranger Things', 'The Office', 'Friends', 'Dark', 'Squid Game']

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const debouncedQuery = useDebounce(query, 400)
  const [trending, setTrending] = useState([])

  useEffect(() => {
    if (!debouncedQuery) {
      getTrending()
        .then(res => setTrending((res.data.results || []).filter(i => i.backdrop_path).slice(0, 12)))
        .catch(() => {})
    }
  }, [debouncedQuery])

  const fetcher = useCallback(
    (page) => searchMulti(debouncedQuery, page),
    [debouncedQuery]
  )
  const { results, loading, sentinelRef, reset } = useInfiniteScroll(fetcher)
  useEffect(() => { reset() }, [debouncedQuery, reset])

  const filtered = results.filter(item => item.media_type === 'movie' || item.media_type === 'tv')

  return (
    <div className="pt-[68px] min-h-screen">
      {/* Header */}
      <div className="px-3 sm:px-6 md:px-12 pt-8 pb-4">
        <h1 className="text-2xl md:text-3xl font-black mb-1">
          {debouncedQuery ? `Results for "${debouncedQuery}"` : 'Search'}
        </h1>
        {!debouncedQuery && (
          <p className="text-gray-500 text-sm">Use the search bar above to find movies, TV shows, anime, and more.</p>
        )}
      </div>

      {/* Trending searches (when no query) */}
      {!debouncedQuery && (
        <div className="px-3 sm:px-6 md:px-12 mb-8">
          <h2 className="text-white font-semibold text-base mb-3">Trending Searches</h2>
          <div className="flex flex-wrap gap-2">
            {TRENDING_SEARCHES.map((term) => (
              <button
                key={term}
                onClick={() => setSearchParams({ q: term })}
                className="flex items-center gap-2 bg-[#2f2f2f] hover:bg-[#3d3d3d] text-white text-sm px-4 py-2 rounded-full transition-colors duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-[#e50914]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                {term}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Trending grid (when no query) */}
      {!debouncedQuery && trending.length > 0 && (
        <div className="px-3 sm:px-6 md:px-12 mb-8">
          <h2 className="text-white font-semibold text-base mb-4">Trending Now</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2">
            {trending.map(item => (
              <MediaCard key={item.id} item={item} isGridItem />
            ))}
          </div>
        </div>
      )}

      {/* No results message */}
      {debouncedQuery && filtered.length === 0 && !loading && (
        <div className="px-3 sm:px-6 md:px-12 text-center py-20">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-gray-400 text-lg mb-2">No results for <strong className="text-white">"{debouncedQuery}"</strong></p>
          <p className="text-gray-600 text-sm">Try different keywords or check your spelling.</p>
        </div>
      )}

      {/* Results grid */}
      {debouncedQuery && (
        <MediaGrid items={filtered} loading={loading} sentinelRef={sentinelRef} />
      )}
    </div>
  )
}
