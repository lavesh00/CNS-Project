import { useParams } from 'react-router-dom'
import useFetch from '../hooks/useFetch'
import { getMovieDetail } from '../services/tmdb'
import MediaInfo from '../components/MediaInfo'
import ContentRow from '../components/ContentRow'
import Loading from '../components/Loading'

export default function MovieDetail() {
  const { id } = useParams()
  const { data: movie, loading } = useFetch(() => getMovieDetail(id), [id])

  if (loading) return <Loading />
  if (!movie) return (
    <div className="pt-[68px] px-12 py-20 text-center">
      <div className="text-5xl mb-4">🎬</div>
      <p className="text-gray-400 text-lg">Movie not found.</p>
    </div>
  )

  const similarFetcher = () =>
    Promise.resolve({ data: { results: movie.similar?.results || [] } })

  const trailers = movie.videos?.results?.filter(v => v.site === 'YouTube' && (v.type === 'Trailer' || v.type === 'Teaser')) || []

  return (
    <div>
      <MediaInfo media={movie} type="movie" />

      {/* Trailers section */}
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
                className="group flex-shrink-0 w-[260px] sm:w-[320px] relative"
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
      {movie.similar?.results?.length > 0 && (
        <div className="mt-4">
          <ContentRow title="More Like This" fetcher={similarFetcher} mediaType="movie" />
        </div>
      )}
    </div>
  )
}
