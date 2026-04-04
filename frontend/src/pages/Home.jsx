import { useState, useEffect } from 'react'
import HeroBanner from '../components/HeroBanner'
import ContentRow from '../components/ContentRow'
import Top10Row from '../components/Top10Row'
import Loading from '../components/Loading'
import {
  getTrending,
  getPopularMovies,
  getPopularTv,
  getTopRatedMovies,
  getTopRatedTv,
  getAnime,
  getKDrama,
  getActionMovies,
  getComedyMovies,
  getHorrorMovies,
  getRomanceMovies,
  getSciFiMovies,
  getDocumentaries,
  getThrillerMovies,
} from '../services/tmdb'

export default function Home() {
  const [heroItems, setHeroItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getTrending()
      .then((res) => {
        const results = res.data.results || []
        const filtered = results.filter((item) => item.backdrop_path)
        setHeroItems(filtered.slice(0, 5))
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <Loading />

  return (
    <div>
      <HeroBanner items={heroItems} />

      <div className="-mt-12 sm:-mt-16 relative z-10 pb-8">
        <ContentRow title="Trending Now" fetcher={getTrending} />
        <ContentRow title="Popular Movies" fetcher={getPopularMovies} mediaType="movie" />
        <Top10Row title="Top 10 in Movies Today" fetcher={getPopularMovies} />
        <ContentRow title="Popular TV Shows" fetcher={getPopularTv} mediaType="tv" />
        <ContentRow title="Top Rated Movies" fetcher={getTopRatedMovies} mediaType="movie" />
        <ContentRow title="Anime" fetcher={getAnime} mediaType="tv" />
        <Top10Row title="Top 10 TV Shows Today" fetcher={getTopRatedTv} />
        <ContentRow title="K-Drama" fetcher={getKDrama} mediaType="tv" />
        <ContentRow title="Action Movies" fetcher={getActionMovies} mediaType="movie" />
        <ContentRow title="Comedy" fetcher={getComedyMovies} mediaType="movie" />
        <ContentRow title="Horror" fetcher={getHorrorMovies} mediaType="movie" />
        <ContentRow title="Romance" fetcher={getRomanceMovies} mediaType="movie" />
        <ContentRow title="Sci-Fi" fetcher={getSciFiMovies} mediaType="movie" />
        <ContentRow title="Top Rated TV" fetcher={getTopRatedTv} mediaType="tv" />
        <ContentRow title="Documentaries" fetcher={getDocumentaries} mediaType="movie" />
        <ContentRow title="Thrillers" fetcher={getThrillerMovies} mediaType="movie" />
      </div>
    </div>
  )
}
