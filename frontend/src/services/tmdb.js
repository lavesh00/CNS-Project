import tmdb from '../config/api'

export const getTrending = (page = 1) =>
  tmdb.get('/trending/all/week', { params: { page } })

export const getPopularMovies = (page = 1) =>
  tmdb.get('/movie/popular', { params: { page } })

export const getPopularTv = (page = 1) =>
  tmdb.get('/tv/popular', { params: { page } })

export const getTopRatedMovies = (page = 1) =>
  tmdb.get('/movie/top_rated', { params: { page } })

export const getTopRatedTv = (page = 1) =>
  tmdb.get('/tv/top_rated', { params: { page } })

export const searchMulti = (query, page = 1) =>
  tmdb.get('/search/multi', { params: { query, page } })

export const getMovieDetail = (id) =>
  tmdb.get(`/movie/${id}`, { params: { append_to_response: 'credits,similar,videos' } })

export const getTvDetail = (id) =>
  tmdb.get(`/tv/${id}`, { params: { append_to_response: 'credits,similar,videos' } })

export const getTvSeason = (id, seasonNumber) =>
  tmdb.get(`/tv/${id}/season/${seasonNumber}`)

export const getMovieGenres = () =>
  tmdb.get('/genre/movie/list')

export const getTvGenres = () =>
  tmdb.get('/genre/tv/list')

export const discoverMovies = (genreId, page = 1) =>
  tmdb.get('/discover/movie', {
    params: { with_genres: genreId, page, sort_by: 'popularity.desc' },
  })

export const discoverTv = (genreId, page = 1) =>
  tmdb.get('/discover/tv', {
    params: { with_genres: genreId, page, sort_by: 'popularity.desc' },
  })

export const getAnime = (page = 1) =>
  tmdb.get('/discover/tv', {
    params: {
      with_genres: 16,
      with_origin_country: 'JP',
      sort_by: 'popularity.desc',
      page,
    },
  })

export const getKDrama = (page = 1) =>
  tmdb.get('/discover/tv', {
    params: {
      with_origin_country: 'KR',
      sort_by: 'popularity.desc',
      page,
    },
  })

export const getActionMovies = (page = 1) =>
  discoverMovies(28, page)

export const getComedyMovies = (page = 1) =>
  discoverMovies(35, page)

export const getHorrorMovies = (page = 1) =>
  discoverMovies(27, page)

export const getRomanceMovies = (page = 1) =>
  discoverMovies(10749, page)

export const getSciFiMovies = (page = 1) =>
  discoverMovies(878, page)

export const getDocumentaries = (page = 1) =>
  discoverMovies(99, page)

export const getThrillerMovies = (page = 1) =>
  discoverMovies(53, page)
