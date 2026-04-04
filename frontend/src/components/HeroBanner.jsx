import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { getTitle, getReleaseDate, getYear, truncateText, formatRating, getMediaType } from '../utils/helpers'
import { IMAGE_BASE, ORIGINAL_SIZE, BACKDROP_SIZE } from '../config/api'
import MaturityBadge from './MaturityBadge'

export default function HeroBanner({ items }) {
  const [current, setCurrent] = useState(0)
  const timerRef = useRef(null)

  // Backwards-compat: accept single item or array
  const list = Array.isArray(items) ? items : (items ? [items] : [])
  const item = list[current]

  useEffect(() => {
    if (list.length <= 1) return
    clearInterval(timerRef.current)
    timerRef.current = setInterval(() => {
      setCurrent((prev) => (prev + 1) % list.length)
    }, 9000)
    return () => clearInterval(timerRef.current)
  }, [list.length])

  if (!item) return null

  const type = getMediaType(item)
  const title = getTitle(item)
  const year = getYear(getReleaseDate(item))
  const overview = truncateText(item.overview, 180)
  const matchScore = Math.round((item.vote_average / 10) * 100)
  const genres = item.genre_ids?.slice(0, 3) || []

  const backdropFull = item.backdrop_path ? `${IMAGE_BASE}${ORIGINAL_SIZE}${item.backdrop_path}` : null
  const backdropSmall = item.backdrop_path ? `${IMAGE_BASE}${BACKDROP_SIZE}${item.backdrop_path}` : null

  const detailPath = type === 'movie' ? `/movie/${item.id}` : `/tv/${item.id}`
  const watchPath = type === 'movie' ? `/watch/movie/${item.id}` : detailPath

  return (
    <div className="relative w-full h-[56vh] sm:h-[62vh] md:h-[76vh] lg:h-[85vh] xl:h-[92vh] overflow-hidden">
      {/* Background image - animate on change */}
      {item.backdrop_path && (
        <picture key={item.id}>
          <source media="(min-width: 1280px)" srcSet={backdropFull} />
          <img
            src={backdropSmall}
            alt={title}
            className="absolute inset-0 w-full h-full object-cover object-top animate-fade-in"
            fetchPriority="high"
          />
        </picture>
      )}

      {/* Layered gradients — Netflix style */}
      <div className="absolute inset-0" style={{
        background: 'linear-gradient(77deg, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0) 50%)'
      }} />
      <div className="absolute inset-0" style={{
        background: 'linear-gradient(to top, #141414 0%, rgba(20,20,20,0.5) 50%, rgba(20,20,20,0) 100%)'
      }} />
      <div className="absolute inset-0" style={{
        background: 'linear-gradient(to bottom, rgba(20,20,20,0.5) 0%, transparent 15%)'
      }} />

      {/* Content */}
      <div className="absolute bottom-[12%] sm:bottom-[16%] left-3 sm:left-6 md:left-12 3xl:left-16 right-3 sm:right-auto max-w-xs sm:max-w-md md:max-w-xl lg:max-w-2xl 3xl:max-w-3xl z-10">

        {/* Type badge */}
        <div className="flex items-center gap-2 mb-2 sm:mb-3 animate-fade-up">
          <div className="flex items-center gap-1">
            <span className="text-[#e50914] font-bold text-xs sm:text-sm tracking-wide uppercase">
              {type === 'movie' ? '🎬 Movie' : '📺 Series'}
            </span>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-black mb-2 sm:mb-4 drop-shadow-2xl leading-tight animate-fade-up delay-100">
          {title}
        </h1>

        {/* Meta row */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-3 sm:mb-4 text-xs sm:text-sm animate-fade-up delay-200">
          <span className="text-[#46d369] font-semibold">{matchScore}% Match</span>
          {year && <span className="text-[#bcbcbc]">{year}</span>}
          <MaturityBadge voteAverage={item.vote_average} adult={item.adult} />
          {type === 'tv' && item.number_of_seasons && (
            <span className="text-[#bcbcbc]">{item.number_of_seasons} Season{item.number_of_seasons !== 1 ? 's' : ''}</span>
          )}
        </div>

        {/* Overview */}
        <p className="hidden sm:block text-[#e5e5e5] text-sm md:text-base 3xl:text-lg mb-4 sm:mb-6 leading-relaxed drop-shadow animate-fade-up delay-200 max-w-lg">
          {overview}
        </p>

        {/* Buttons */}
        <div className="flex items-center gap-2 sm:gap-3 animate-fade-up delay-300">
          <Link to={watchPath} className="btn-nf-white text-sm sm:text-base px-4 sm:px-6 py-2 sm:py-2.5">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z" />
            </svg>
            Play
          </Link>
          <Link to={detailPath} className="btn-nf-gray text-sm sm:text-base px-4 sm:px-6 py-2 sm:py-2.5">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 sm:h-5 sm:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            More Info
          </Link>
        </div>
      </div>

      {/* Cycle dots */}
      {list.length > 1 && (
        <div className="absolute bottom-3 right-4 flex gap-1.5 z-10">
          {list.map((_, i) => (
            <button
              key={i}
              onClick={() => { setCurrent(i); clearInterval(timerRef.current) }}
              className={`w-2 h-0.5 rounded-full transition-all duration-300 ${i === current ? 'bg-white w-4' : 'bg-white/40'}`}
              aria-label={`Show item ${i + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  )
}
