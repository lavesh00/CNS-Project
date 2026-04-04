import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { getImageUrl, getTitle, getMediaType } from '../utils/helpers'

export default function Top10Row({ title, fetcher }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const rowRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    fetcher()
      .then((res) => {
        if (!cancelled) {
          setItems((res.data.results || []).slice(0, 10))
          setLoading(false)
        }
      })
      .catch(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  if (loading) {
    return (
      <div className="px-3 sm:px-6 md:px-12 mb-6 sm:mb-8">
        <div className="h-5 w-40 skeleton rounded mb-3" />
        <div className="flex gap-1 overflow-hidden">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="flex-shrink-0 w-[200px] sm:w-[250px] h-[130px] sm:h-[160px] skeleton rounded-md" />
          ))}
        </div>
      </div>
    )
  }

  if (!items.length) return null

  return (
    <div className="mb-6 sm:mb-8">
      <h2 className="text-white text-sm sm:text-base md:text-lg font-semibold px-3 sm:px-6 md:px-12 mb-1 sm:mb-2">
        {title}
      </h2>
      <div
        ref={rowRef}
        className="flex overflow-x-auto hide-scrollbar px-3 sm:px-6 md:px-12 py-2 sm:py-4"
      >
        {items.map((item, idx) => {
          const type = getMediaType(item)
          const ttl = getTitle(item)
          const detailPath = type === 'movie' ? `/movie/${item.id}` : `/tv/${item.id}`
          const poster = getImageUrl(item.poster_path)
          return (
            <Link
              key={item.id}
              to={detailPath}
              className="group relative flex-shrink-0 flex items-end"
              style={{ width: 'clamp(120px, 14vw, 200px)' }}
            >
              {/* Big rank number */}
              <span
                className="top10-num select-none"
                style={{ lineHeight: 0.85, marginRight: '-10px', zIndex: 1, flexShrink: 0 }}
              >
                {idx + 1}
              </span>
              {/* Poster */}
              <div className="relative flex-1 rounded-md overflow-hidden shadow-xl transition-transform duration-300 group-hover:scale-105 group-hover:z-10">
                <div className="aspect-[2/3]">
                  <img
                    src={poster}
                    alt={ttl}
                    loading="lazy"
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
