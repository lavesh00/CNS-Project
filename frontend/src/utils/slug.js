export function generateSlug(title, year) {
  if (!title) return ''
  let slug = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
  if (year) {
    slug += `-${year}`
  }
  return slug
}

export function buildAnimeEmbedUrl(titleSlug, episode, server) {
  let url = `https://anime.autoembed.cc/embed/${titleSlug}-episode-${episode}`
  if (server && server > 1) url += `?server=${server}`
  return url
}

export function buildDramaEmbedUrl(titleSlug, episode, server) {
  let url = `https://drama.autoembed.cc/embed/${titleSlug}-episode-${episode}`
  if (server && server > 1) url += `?server=${server}`
  return url
}

export function buildMovieEmbedUrl(id, server) {
  let url = `https://player.autoembed.app/embed/movie/${id}`
  if (server && server > 1) url += `?server=${server}`
  return url
}

export function buildTvEmbedUrl(id, season, episode, server) {
  let url = `https://player.autoembed.app/embed/tv/${id}/${season}/${episode}`
  if (server && server > 1) url += `?server=${server}`
  return url
}
