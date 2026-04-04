import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getTitle, getReleaseDate, getYear, formatRating, getMediaType } from '../utils/helpers'
import { getImageUrl } from '../utils/helpers'
import { BACKDROP_SIZE } from '../config/api'
import MaturityBadge from './MaturityBadge'

export default function HoverCard({ item, mediaType, anchorRect, onClose }) {
  const cardRef = useRef(null)
  const navigate = useNavigate()
  const type = mediaType || getMediaType(item)
  const title = getTitle(item)
  const year = getYear(getReleaseDate(item))
  const rating = formatRating(item.vote_average)
  const matchScore = Math.round((item.vote_average / 10) * 100)
  const genres = item.genre_ids || []
  const detailPath = type === 'movie' ? `/movie/${item.id}` : `/tv/${item.id}`
  const watchPath = type === 'movie' ? `/watch/movie/${item.id}` : detailPath
  const image = item.backdrop_path
    ? getImageUrl(item.backdrop_path, BACKDROP_SIZE)
    : getImageUrl(item.poster_path)

  // Position logic: stay inside viewport
  const [style, setStyle] = useState({ opacity: 0 })
  useEffect(() => {
    if (!anchorRect || !cardRef.current) return
    const CARD_W = 320
    const CARD_H = cardRef.current.offsetHeight || 280
    const vw = window.innerWidth
    const scale = 1.25

    let left = anchorRect.left + anchorRect.width / 2 - CARD_W / 2
    if (left < 8) left = 8
    if (left + CARD_W > vw - 8) left = vw - CARD_W - 8

    // Position vertically: prefer below anchor, flip above if not enough space
    let top = anchorRect.top + window.scrollY - CARD_H / 2 + anchorRect.height / 2
    if (top + CARD_H > window.scrollY + window.innerHeight - 16) {
      top = anchorRect.top + window.scrollY - CARD_H + anchorRect.height / 2
    }
    if (top - window.scrollY < 80) top = window.scrollY + 80

    setStyle({ position: 'absolute', top, left, width: CARD_W, zIndex: 9999, opacity: 1 })
  }, [anchorRect])

  return (
    <div
      ref={cardRef}
      style={style}
      className="animate-hover-card bg-[#181818] rounded-md shadow-2xl overflow-hidden border border-white/10"
      onMouseLeave={onClose}
    >
      {/* Thumbnail */}
      <div className="relative aspect-video">
        <img
          src={image}
          alt={title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#181818] via-transparent to-transparent" />
      </div>

      <div className="px-4 py-3">
        {/* Actions row */}
        <div className="flex items-center gap-2 mb-3">
          <button
            onClick={() => { navigate(watchPath); onClose() }}
            className="btn-icon"
            style={{ width: 36, height: 36, background: 'white', border: 'none' }}
            title="Play"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="black">
              <path d="M8 5v14l11-7z" />
            </svg>
          </button>
          <button className="btn-icon" title="Add to My List">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
          </button>
          <button className="btn-icon" title="Like">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
            </svg>
          </button>
          <Link
            to={detailPath}
            onClick={onClose}
            className="btn-icon ml-auto"
            title="More Info"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </Link>
        </div>

        {/* Meta */}
        <h3 className="text-white font-semibold text-sm mb-1.5 line-clamp-1">{title}</h3>
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <span className="text-green-400 font-semibold text-xs">{matchScore}% Match</span>
          {year && <span className="text-gray-400 text-xs">{year}</span>}
          <MaturityBadge voteAverage={item.vote_average} adult={item.adult} />
          <span className="text-gray-400 text-xs border border-gray-600 px-1 rounded-sm">
            {type === 'movie' ? 'Movie' : 'Series'}
          </span>
        </div>
      </div>
    </div>
  )
}
