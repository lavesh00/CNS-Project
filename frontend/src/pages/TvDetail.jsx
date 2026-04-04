import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import useFetch from '../hooks/useFetch'
import { getTvDetail, getTvSeason } from '../services/tmdb'
import MediaInfo from '../components/MediaInfo'
import SeasonSelector from '../components/SeasonSelector'
import ContentRow from '../components/ContentRow'
import Loading from '../components/Loading'

export default function TvDetail() {
  const { id } = useParams()
  const { data: show, loading } = useFetch(() => getTvDetail(id), [id])
  const [selectedSeason, setSelectedSeason] = useState(1)
  const [episodes, setEpisodes] = useState([])
  const [episodesLoading, setEpisodesLoading] = useState(false)

  const isAnime = show?.origin_country?.includes('JP') && show?.genres?.some((g) => g.id === 16)
  const isDrama = show?.origin_country?.includes('KR')

  useEffect(() => {
    if (!show) return
    const firstSeason = show.seasons?.find((s) => s.season_number > 0)
    if (firstSeason) setSelectedSeason(firstSeason.season_number)
  }, [show])

  useEffect(() => {
    if (!id || !selectedSeason) return
    setEpisodesLoading(true)
    getTvSeason(id, selectedSeason)
      .then((res) => {
        setEpisodes(res.data.episodes || [])
        setEpisodesLoading(false)
      })
      .catch(() => setEpisodesLoading(false))
  }, [id, selectedSeason])

  if (loading) return <Loading />
  if (!show) return (
    <div className="pt-[68px] px-12 py-20 text-center">
      <div className="text-5xl mb-4">📺</div>
      <p className="text-gray-400 text-lg">Show not found.</p>
    </div>
  )

  const similarFetcher = () =>
    Promise.resolve({ data: { results: show.similar?.results || [] } })

  const trailers = show.videos?.results?.filter(v => v.site === 'YouTube' && (v.type === 'Trailer' || v.type === 'Teaser')) || []

  return (
    <div>
      <MediaInfo media={show} type="tv" />

      <SeasonSelector
        seasons={show.seasons}
        episodes={episodes}
        selectedSeason={selectedSeason}
        onSeasonChange={setSelectedSeason}
        showId={id}
        isAnime={isAnime}
        isDrama={isDrama}
      />

      {episodesLoading && (
        <div className="px-3 sm:px-6 md:px-12 mt-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 skeleton rounded-md mb-3" />
          ))}
        </div>
      )}

      {/* Trailers */}
      {trailers.length > 0 && (
        <div className="px-3 sm:px-6 md:px-12 mt-6 mb-4">
          <h2 className="text-white font-semibold text-base sm:text-lg mb-3">Trailers &amp; More</h2>
          <div className="flex gap-3 overflow-x-auto hide-scrollbar pb-2">
            {trailers.map((trailer) => (
              <a
                key={trailer.key}
                href={`https://www.youtube.com/watch?v=${trailer.key}`}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex-shrink-0 w-[260px] sm:w-[320px]"
              >
                <div className="aspect-video rounded-md overflow-hidden bg-[#181818] relative">
                  <img
                    src={`https://img.youtube.com/vi/${trailer.key}/mqdefault.jpg`}
                    alt={trailer.name}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/40 transition-colors">
                    <div className="bg-white/90 rounded-full p-3 group-hover:scale-110 transition-transform">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-black" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </div>
                  </div>
                </div>
                <p className="text-gray-300 text-xs mt-1.5 line-clamp-1">{trailer.name}</p>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* More like this */}
      {show.similar?.results?.length > 0 && (
        <div className="mt-4">
          <ContentRow title="More Like This" fetcher={similarFetcher} mediaType="tv" />
        </div>
      )}
    </div>
  )
}
