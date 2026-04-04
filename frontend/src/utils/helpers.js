import { IMAGE_BASE, POSTER_SIZE, BACKDROP_SIZE } from '../config/api'

const PLACEHOLDER_POSTER = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="342" height="513" fill="%23181818"%3E%3Crect width="342" height="513"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%23555" font-size="16"%3ENo Image%3C/text%3E%3C/svg%3E'

export function getImageUrl(path, size = POSTER_SIZE) {
  if (!path) return PLACEHOLDER_POSTER
  return `${IMAGE_BASE}${size}${path}`
}

export function getBackdropUrl(path) {
  if (!path) return null
  return `${IMAGE_BASE}${BACKDROP_SIZE}${path}`
}

export function formatRating(vote) {
  if (!vote) return 'N/A'
  return vote.toFixed(1)
}

export function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

export function getYear(dateString) {
  if (!dateString) return ''
  return new Date(dateString).getFullYear()
}

export function truncateText(text, maxLength = 150) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trim() + '...'
}

export function getMediaType(item) {
  if (item.media_type) return item.media_type
  if (item.title) return 'movie'
  if (item.name) return 'tv'
  return 'movie'
}

export function getTitle(item) {
  return item.title || item.name || 'Untitled'
}

export function getReleaseDate(item) {
  return item.release_date || item.first_air_date || ''
}

export function getRuntimeText(runtime) {
  if (!runtime) return ''
  const hours = Math.floor(runtime / 60)
  const minutes = runtime % 60
  if (hours === 0) return `${minutes}m`
  return `${hours}h ${minutes}m`
}
