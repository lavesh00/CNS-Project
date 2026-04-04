import { useState, useEffect, useRef, useCallback } from 'react'

export default function useInfiniteScroll(fetcher) {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [hasMore, setHasMore] = useState(true)
  const sentinelRef = useRef(null)
  const pageRef = useRef(1)
  const loadingRef = useRef(false)

  const loadMore = useCallback(() => {
    if (loadingRef.current || !hasMore) return
    loadingRef.current = true
    setLoading(true)
    setError(null)

    const currentPage = pageRef.current

    fetcher(currentPage)
      .then((res) => {
        const newResults = res.data.results || []
        setResults((prev) => {
          const existingIds = new Set(prev.map((item) => item.id))
          const unique = newResults.filter((item) => !existingIds.has(item.id))
          return [...prev, ...unique]
        })
        const totalPages = res.data.total_pages || 1
        setHasMore(currentPage < totalPages)
        pageRef.current = currentPage + 1
        loadingRef.current = false
        setLoading(false)
      })
      .catch((err) => {
        setError(err?.message || 'Failed to load content')
        loadingRef.current = false
        setLoading(false)
      })
  }, [hasMore, fetcher])

  useEffect(() => {
    const sentinel = sentinelRef.current
    if (!sentinel) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMore()
        }
      },
      { threshold: 0.1, rootMargin: '200px' }
    )
    observer.observe(sentinel)
    return () => observer.disconnect()
  }, [loadMore])

  const reset = useCallback(() => {
    setResults([])
    pageRef.current = 1
    loadingRef.current = false
    setHasMore(true)
    setLoading(false)
    setError(null)
  }, [])

  return { results, loading, hasMore, error, sentinelRef, reset }
}
