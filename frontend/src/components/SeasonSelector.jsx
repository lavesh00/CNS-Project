import { Link } from 'react-router-dom'
import { getImageUrl } from '../utils/helpers'
import { BACKDROP_SIZE } from '../config/api'

export default function SeasonSelector({ seasons, episodes, selectedSeason, onSeasonChange, showId, isAnime, isDrama }) {
  const filteredSeasons = seasons?.filter((s) => s.season_number > 0) || []

  return (
    <div className="px-3 sm:px-6 md:px-12 3xl:px-16 mt-6 sm:mt-8">
      {/* Season tabs */}
      <div className="flex items-center gap-4 mb-4 sm:mb-6 border-b border-gray-800">
        <h3 className="text-white text-base sm:text-lg font-semibold pb-2 border-b-2 border-transparent mr-2">
          Episodes
        </h3>
        {filteredSeasons.length > 1 && (
          <div className="flex gap-1 overflow-x-auto hide-scrollbar pb-0.5">
            {filteredSeasons.map((s) => (
              <button
                key={s.season_number}
                onClick={() => onSeasonChange(s.season_number)}
                className={`flex-shrink-0 px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-sm transition-all duration-200 ${
                  s.season_number === selectedSeason
                    ? 'bg-[#e50914] text-white'
                    : 'text-gray-400 hover:text-white hover:bg-[#2f2f2f]'
                }`}
              >
                S{s.season_number}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Episode list */}
      <div className="space-y-2 sm:space-y-2.5">
        {episodes?.map((ep) => {
          let watchPath
          if (isAnime) watchPath = `/watch/anime/${showId}?episode=${ep.episode_number}&season=${selectedSeason}`
          else if (isDrama) watchPath = `/watch/drama/${showId}?episode=${ep.episode_number}&season=${selectedSeason}`
          else watchPath = `/watch/tv/${showId}/${selectedSeason}/${ep.episode_number}`

          return (
            <Link
              key={ep.id}
              to={watchPath}
              className="flex items-center gap-2 sm:gap-4 bg-[#181818] hover:bg-[#252525] rounded-md p-2.5 sm:p-3.5 transition-all duration-200 group border border-transparent hover:border-white/5"
            >
              {/* Episode number */}
              <span className="text-gray-500 text-sm sm:text-base font-bold w-6 sm:w-8 text-center flex-shrink-0 group-hover:text-white transition-colors">
                {ep.episode_number}
              </span>

              {/* Thumbnail */}
              <div className="hidden sm:block flex-shrink-0 w-28 md:w-36 aspect-video rounded overflow-hidden bg-[#2f2f2f] relative">
                {ep.still_path ? (
                  <img
                    src={getImageUrl(ep.still_path, BACKDROP_SIZE)}
                    alt={ep.name}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-700 text-xs">No Preview</div>
                )}
                {/* Play overlay */}
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/30">
                  <div className="bg-white/90 rounded-full p-1.5 sm:p-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 sm:h-5 sm:w-5 text-black" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <h4 className="text-white text-xs sm:text-sm font-medium line-clamp-1 group-hover:text-white">
                  {ep.name || `Episode ${ep.episode_number}`}
                </h4>
                {ep.runtime && (
                  <span className="text-gray-500 text-[10px] sm:text-xs">{ep.runtime}m</span>
                )}
                {ep.overview && (
                  <p className="text-gray-500 text-[10px] sm:text-xs mt-0.5 sm:mt-1 line-clamp-1 sm:line-clamp-2">{ep.overview}</p>
                )}
              </div>

              {/* Mobile play icon */}
              <div className="sm:hidden flex-shrink-0 text-gray-600 group-hover:text-[#e50914] transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
