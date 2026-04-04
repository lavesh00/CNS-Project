import { useState, useEffect } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import VideoPlayer from '../components/VideoPlayer'
import ServerSelector from '../components/ServerSelector'
import { buildMovieEmbedUrl, buildTvEmbedUrl, buildAnimeEmbedUrl, buildDramaEmbedUrl, generateSlug } from '../utils/slug'
import { getMovieDetail, getTvDetail, getTvSeason } from '../services/tmdb'
import { getYear } from '../utils/helpers'
import { getImageUrl } from '../utils/helpers'

export default function Watch() {
  const { id, season, episode } = useParams()
  const [searchParams] = useSearchParams()
  const [server, setServer] = useState(1)
  const [embedUrl, setEmbedUrl] = useState('')
  const [title, setTitle] = useState('')
  const [mediaInfo, setMediaInfo] = useState(null)
  const [episodes, setEpisodes] = useState([])
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const path = window.location.pathname
  const isMovie = path.startsWith('/watch/movie/')
  const isTv = path.startsWith('/watch/tv/')
  const isAnime = path.startsWith('/watch/anime/')
  const isDrama = path.startsWith('/watch/drama/')

  const currentEp = isTv ? Number(episode) : Number(searchParams.get('episode') || 1)
  const currentSeason = isTv ? Number(season) : Number(searchParams.get('season') || 1)

  useEffect(() => {
    if (isMovie) {
      setEmbedUrl(buildMovieEmbedUrl(id, server))
      getMovieDetail(id).then((res) => { setTitle(res.data.title); setMediaInfo(res.data) }).catch(() => {})
    } else if (isTv) {
      setEmbedUrl(buildTvEmbedUrl(id, season, episode, server))
      getTvDetail(id).then((res) => {
        setTitle(`${res.data.name} · S${season}E${episode}`)
        setMediaInfo(res.data)
        // Load episode list
        getTvSeason(id, season).then(s => setEpisodes(s.data.episodes || [])).catch(() => {})
      }).catch(() => {})
    } else if (isAnime || isDrama) {
      const ep = searchParams.get('episode') || '1'
      getTvDetail(id).then((res) => {
        const show = res.data
        const name = show.name || show.original_name
        const year = getYear(show.first_air_date)
        const slug = generateSlug(name, year)
        setTitle(`${name} · Episode ${ep}`)
        setMediaInfo(show)
        if (isAnime) setEmbedUrl(buildAnimeEmbedUrl(slug, ep, server))
        else setEmbedUrl(buildDramaEmbedUrl(slug, ep, server))
        // Load episode list for season 1 by default
        getTvSeason(id, currentSeason).then(s => setEpisodes(s.data.episodes || [])).catch(() => {})
      }).catch(() => {})
    }
  }, [id, season, episode, server, isMovie, isTv, isAnime, isDrama, searchParams])

  const backPath = isMovie ? `/movie/${id}` : `/tv/${id}`

  return (
    <div className="min-h-screen bg-black pt-[68px]">
      <div className="max-w-[1600px] mx-auto px-2 sm:px-4 py-4">
        {/* Back + Title */}
        <div className="flex items-center gap-3 mb-3">
          <Link
            to={backPath}
            className="flex items-center gap-1 text-gray-400 hover:text-white transition-colors text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </Link>
          {title && (
            <h1 className="text-white text-sm sm:text-base font-semibold truncate">{title}</h1>
          )}
          {(isTv || isAnime || isDrama) && episodes.length > 0 && (
            <button
              onClick={() => setSidebarOpen(v => !v)}
              className="ml-auto text-gray-400 hover:text-white transition-colors text-xs flex items-center gap-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h8m-8 6h16" />
              </svg>
              Episodes
            </button>
          )}
        </div>

        {/* Main content area */}
        <div className={`flex gap-4 ${(isTv || isAnime || isDrama) && episodes.length > 0 && sidebarOpen ? 'flex-col lg:flex-row' : ''}`}>
          {/* Player */}
          <div className="flex-1 min-w-0">
            {embedUrl && <VideoPlayer src={embedUrl} />}

            {/* Server Selector */}
            <div className="mt-3">
              <ServerSelector currentServer={server} onServerChange={setServer} />
            </div>

            {/* Episode nav for TV */}
            {isTv && (
              <div className="flex items-center gap-2 mt-3 flex-wrap">
                {Number(episode) > 1 && (
                  <Link
                    to={`/watch/tv/${id}/${season}/${Number(episode) - 1}`}
                    className="flex items-center gap-1.5 px-4 py-2 bg-[#2f2f2f] hover:bg-[#404040] text-white rounded transition text-sm"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Prev Episode
                  </Link>
                )}
                <Link
                  to={`/watch/tv/${id}/${season}/${Number(episode) + 1}`}
                  className="flex items-center gap-1.5 px-4 py-2 bg-[#e50914] hover:bg-[#f6121d] text-white rounded transition text-sm font-semibold"
                >
                  Next Episode
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            )}

            {/* Anime/Drama nav */}
            {(isAnime || isDrama) && (
              <div className="flex items-center gap-2 mt-3 flex-wrap">
                {Number(searchParams.get('episode')) > 1 && (
                  <Link
                    to={`/watch/${isAnime ? 'anime' : 'drama'}/${id}?episode=${Number(searchParams.get('episode')) - 1}&season=${searchParams.get('season') || '1'}`}
                    className="flex items-center gap-1.5 px-4 py-2 bg-[#2f2f2f] hover:bg-[#404040] text-white rounded transition text-sm"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Prev
                  </Link>
                )}
                <Link
                  to={`/watch/${isAnime ? 'anime' : 'drama'}/${id}?episode=${Number(searchParams.get('episode') || '1') + 1}&season=${searchParams.get('season') || '1'}`}
                  className="flex items-center gap-1.5 px-4 py-2 bg-[#e50914] hover:bg-[#f6121d] text-white rounded transition text-sm font-semibold"
                >
                  Next Episode
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            )}
          </div>

          {/* Episode Sidebar (TV/Anime/Drama only) */}
          {(isTv || isAnime || isDrama) && episodes.length > 0 && sidebarOpen && (
            <div className="lg:w-80 xl:w-96 flex-shrink-0">
              <div className="bg-[#181818] rounded-md overflow-hidden">
                <div className="px-4 py-3 bg-[#2f2f2f] flex items-center justify-between">
                  <h3 className="text-white font-semibold text-sm">
                    Episodes {isTv ? `· Season ${season}` : ''}
                  </h3>
                  <span className="text-gray-500 text-xs">{episodes.length} eps</span>
                </div>
                <div className="overflow-y-auto" style={{ maxHeight: '65vh' }}>
                  {episodes.map((ep) => {
                    const watchPath = isTv
                      ? `/watch/tv/${id}/${season}/${ep.episode_number}`
                      : `/watch/${isAnime ? 'anime' : 'drama'}/${id}?episode=${ep.episode_number}&season=${currentSeason}`
                    const isCurrentEp = ep.episode_number === currentEp
                    return (
                      <Link
                        key={ep.id}
                        to={watchPath}
                        className={`flex items-center gap-3 p-3 border-b border-black/30 transition-colors ${
                          isCurrentEp ? 'bg-[#e50914]/20 border-l-2 border-l-[#e50914]' : 'hover:bg-[#2f2f2f]'
                        }`}
                      >
                        <span className={`text-sm font-bold w-6 text-center flex-shrink-0 ${isCurrentEp ? 'text-[#e50914]' : 'text-gray-500'}`}>
                          {ep.episode_number}
                        </span>
                        {ep.still_path && (
                          <div className="flex-shrink-0 w-20 aspect-video rounded overflow-hidden bg-[#2f2f2f]">
                            <img
                              src={getImageUrl(ep.still_path, 'w300')}
                              alt={ep.name}
                              className="w-full h-full object-cover"
                              loading="lazy"
                            />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <p className={`text-xs font-medium line-clamp-1 ${isCurrentEp ? 'text-white' : 'text-gray-300'}`}>
                            {ep.name || `Episode ${ep.episode_number}`}
                          </p>
                          {ep.runtime && (
                            <p className="text-gray-600 text-[10px] mt-0.5">{ep.runtime}m</p>
                          )}
                        </div>
                        {isCurrentEp && (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-[#e50914] flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M8 5v14l11-7z" />
                          </svg>
                        )}
                      </Link>
                    )
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
