import { useState, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { getImageUrl, getTitle, getReleaseDate, getYear, formatRating, getMediaType } from '../utils/helpers'
import { BACKDROP_SIZE } from '../config/api'
import HoverCard from './HoverCard'

let hoverTimer = null

export default function MediaCard({ item, mediaType, isGridItem }) {
  const [imgError, setImgError] = useState(false)
  const [showHover, setShowHover] = useState(false)
  const [anchorRect, setAnchorRect] = useState(null)
  const cardRef = useRef(null)

  const type = mediaType || getMediaType(item)
  const title = getTitle(item)
  const year = getYear(getReleaseDate(item))
  const rating = formatRating(item.vote_average)
  const matchScore = Math.round((item.vote_average / 10) * 100)
  const detailPath = type === 'movie' ? `/movie/${item.id}` : `/tv/${item.id}`

  const image = !imgError && item.backdrop_path
    ? getImageUrl(item.backdrop_path, BACKDROP_SIZE)
    : getImageUrl(item.poster_path)

  const handleMouseEnter = useCallback(() => {
    hoverTimer = setTimeout(() => {
      if (cardRef.current) {
        setAnchorRect(cardRef.current.getBoundingClientRect())
        setShowHover(true)
      }
    }, 400)
  }, [])

  const handleMouseLeave = useCallback(() => {
    clearTimeout(hoverTimer)
    // Don't hide immediately — HoverCard handles its own onMouseLeave
  }, [])

  const closeHover = useCallback(() => {
    clearTimeout(hoverTimer)
    setShowHover(false)
    setAnchorRect(null)
  }, [])

  const cardClass = isGridItem
    ? 'group relative rounded-md overflow-hidden cursor-pointer transition-transform duration-300 hover:scale-105 hover:z-20'
    : 'group relative flex-shrink-0 w-[140px] sm:w-[195px] md:w-[234px] lg:w-[258px] xl:w-[280px] 3xl:w-[320px] rounded-md overflow-hidden cursor-pointer transition-transform duration-300'

  return (
    <>
      <div
        ref={cardRef}
        className={cardClass}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <Link to={detailPath} className="block">
          {/* Image */}
          <div className="aspect-video bg-[#181818] overflow-hidden">
            <img
              src={image}
              alt={title}
              loading="lazy"
              onError={() => setImgError(true)}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>

          {/* Match score badge (top right) */}
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <span className="text-[#46d369] text-[10px] font-bold bg-black/70 px-1.5 py-0.5 rounded-sm">
              {matchScore}%
            </span>
          </div>

          {/* Bottom gradient overlay on hover */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-2 sm:p-3">
            <h3 className="text-white text-xs sm:text-sm font-semibold line-clamp-1">{title}</h3>
            <div className="flex items-center gap-1.5 mt-0.5 text-[10px] sm:text-xs">
              <span className="text-[#46d369] font-semibold">{rating}</span>
              {year && <span className="text-gray-400">{year}</span>}
            </div>
          </div>
        </Link>

        {/* Mobile: title below */}
        <div className="sm:hidden bg-[#181818] px-2 py-1.5">
          <p className="text-white text-xs line-clamp-1">{title}</p>
        </div>
      </div>

      {/* Hover Card Portal — desktop only */}
      {showHover && anchorRect && (
        <div className="fixed inset-0 z-[9998] pointer-events-none hidden sm:block">
          <div className="pointer-events-auto">
            <HoverCard
              item={item}
              mediaType={type}
              anchorRect={anchorRect}
              onClose={closeHover}
            />
          </div>
        </div>
      )}
    </>
  )
}
