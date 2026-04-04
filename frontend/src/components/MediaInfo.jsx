import { useState } from 'react'
import { Link } from 'react-router-dom'
import { getImageUrl, formatRating, getYear, getRuntimeText } from '../utils/helpers'
import { IMAGE_BASE, ORIGINAL_SIZE, BACKDROP_SIZE, PROFILE_SIZE } from '../config/api'
import MaturityBadge from './MaturityBadge'

export default function MediaInfo({ media, type }) {
  const [activeTab, setActiveTab] = useState('episodes')
  if (!media) return null

  const title = media.title || media.name
  const year = getYear(media.release_date || media.first_air_date)
  const rating = formatRating(media.vote_average)
  const matchScore = Math.round((media.vote_average / 10) * 100)
  const runtime = type === 'movie' ? getRuntimeText(media.runtime) : `${media.number_of_seasons} Season${media.number_of_seasons !== 1 ? 's' : ''}`
  const genres = media.genres || []
  const cast = media.credits?.cast?.slice(0, 12) || []
  const trailers = media.videos?.results?.filter(v => v.site === 'YouTube' && (v.type === 'Trailer' || v.type === 'Teaser')).slice(0, 4) || []
  const backdropFull = media.backdrop_path ? `${IMAGE_BASE}${ORIGINAL_SIZE}${media.backdrop_path}` : null
  const backdropSmall = media.backdrop_path ? `${IMAGE_BASE}${BACKDROP_SIZE}${media.backdrop_path}` : null
  const watchPath = type === 'movie' ? `/watch/movie/${media.id}` : null

  const tabs = [
    ...(type === 'tv' ? [{ id: 'episodes', label: 'Episodes' }] : []),
    { id: 'more', label: 'More Like This' },
    ...(trailers.length > 0 ? [{ id: 'trailers', label: 'Trailers & More' }] : []),
  ]

  return (
    <div>
      {/* Cinematic backdrop */}
      <div className="relative w-full h-[38vh] sm:h-[45vh] md:h-[58vh] lg:h-[65vh] xl:h-[70vh]">
        {media.backdrop_path && (
          <picture>
            <source media="(min-width: 1280px)" srcSet={backdropFull} />
            <img src={backdropSmall} alt={title} className="absolute inset-0 w-full h-full object-cover" />
          </picture>
        )}
        <div className="absolute inset-0" style={{ background: 'linear-gradient(to top, #141414 0%, rgba(20,20,20,0.6) 50%, rgba(20,20,20,0) 100%)' }} />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(77deg, rgba(0,0,0,0.6) 0%, transparent 60%)' }} />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(to bottom, rgba(20,20,20,0.4) 0%, transparent 20%)' }} />
      </div>

      {/* Info panel */}
      <div className="px-3 sm:px-6 md:px-12 3xl:px-16 -mt-[180px] sm:-mt-[200px] md:-mt-[240px] relative z-10">
        <div className="flex flex-col md:flex-row gap-6 md:gap-10 xl:gap-14">
          {/* Poster */}
          <div className="hidden md:block flex-shrink-0">
            <img
              src={getImageUrl(media.poster_path)}
              alt={title}
              className="w-40 lg:w-52 xl:w-60 3xl:w-72 rounded-lg shadow-2xl ring-1 ring-white/10"
            />
          </div>

          {/* Text */}
          <div className="flex-1 max-w-3xl 3xl:max-w-4xl">
            {/* Title */}
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black mb-3 leading-tight">
              {title}
            </h1>

            {/* Meta */}
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-3 text-xs sm:text-sm">
              <span className="text-[#46d369] font-bold text-base">{matchScore}% Match</span>
              {year && <span className="text-[#bcbcbc]">{year}</span>}
              {runtime && <span className="text-[#bcbcbc]">{runtime}</span>}
              <MaturityBadge voteAverage={media.vote_average} adult={media.adult} />
            </div>

            {/* Genres */}
            <div className="flex flex-wrap gap-1.5 mb-4">
              {genres.map((g) => (
                <span key={g.id} className="px-3 py-1 bg-[#2f2f2f] hover:bg-[#3d3d3d] text-gray-300 text-xs rounded-full transition-colors cursor-default">
                  {g.name}
                </span>
              ))}
            </div>

            {/* Tagline */}
            {media.tagline && (
              <p className="text-gray-400 italic text-sm mb-3">"{media.tagline}"</p>
            )}

            {/* Overview */}
            <p className="text-[#d2d2d2] text-sm md:text-base leading-relaxed mb-6 max-w-2xl">
              {media.overview}
            </p>

            {/* Rating bar */}
            <div className="flex items-center gap-3 mb-5">
              <span className="text-gray-400 text-xs">Rating</span>
              <div className="flex-1 max-w-[180px] h-1 bg-gray-700 rounded-full overflow-hidden">
                <div className="match-bar-fill h-full" style={{ width: `${matchScore}%` }} />
              </div>
              <span className="text-[#46d369] font-semibold text-sm">{rating}</span>
            </div>

            {/* Action buttons */}
            <div className="flex flex-wrap items-center gap-3 mb-6">
              {watchPath && (
                <Link to={watchPath} className="btn-nf-white text-sm sm:text-base px-5 sm:px-7 py-2 sm:py-2.5">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                  Play
                </Link>
              )}
              <button className="btn-icon" style={{ width: 42, height: 42 }} title="Add to My List">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
              </button>
              <button className="btn-icon" style={{ width: 42, height: 42 }} title="Like">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                </svg>
              </button>
            </div>

            {/* Cast */}
            {cast.length > 0 && (
              <div className="mb-2">
                <p className="text-gray-500 text-xs sm:text-sm mb-3">
                  <span className="text-gray-400 font-semibold">Cast: </span>
                  {cast.slice(0, 5).map(p => p.name).join(', ')}
                  {cast.length > 5 && <span className="text-gray-600"> and more</span>}
                </p>
                <div className="flex gap-3 overflow-x-auto hide-scrollbar pb-2">
                  {cast.map((person) => (
                    <div key={person.id} className="flex-shrink-0 text-center w-16 sm:w-20">
                      <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-full overflow-hidden mx-auto mb-1 bg-[#2f2f2f] ring-1 ring-white/10">
                        <img
                          src={person.profile_path ? getImageUrl(person.profile_path, PROFILE_SIZE) : 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22185%22 height=%22278%22 fill=%22%23282828%22%3E%3Crect width=%22185%22 height=%22278%22/%3E%3C/svg%3E'}
                          alt={person.name}
                          loading="lazy"
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <p className="text-[10px] sm:text-xs text-gray-300 line-clamp-1">{person.name}</p>
                      <p className="text-[10px] sm:text-xs text-gray-600 line-clamp-1">{person.character}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Tab strip */}
        {tabs.length > 0 && (
          <div className="mt-8 border-b border-gray-800">
            <div className="flex gap-0 overflow-x-auto hide-scrollbar">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  className={`nf-tab ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
