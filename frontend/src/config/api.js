import axios from 'axios'

const API_KEY = import.meta.env.VITE_TMDB_API_KEY

const tmdb = axios.create({
  baseURL: 'https://api.themoviedb.org/3',
  params: {
    api_key: API_KEY,
  },
})

export const IMAGE_BASE = 'https://image.tmdb.org/t/p/'
export const POSTER_SIZE = 'w342'
export const BACKDROP_SIZE = 'w1280'
export const ORIGINAL_SIZE = 'original'
export const PROFILE_SIZE = 'w185'

export default tmdb
