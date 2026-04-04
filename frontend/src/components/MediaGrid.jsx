import MediaCard from './MediaCard'

export default function MediaGrid({ items, loading, sentinelRef, mediaType }) {
  return (
    <div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7 3xl:grid-cols-8 4xl:grid-cols-9 gap-2 sm:gap-3 md:gap-4 px-3 sm:px-6 md:px-12 3xl:px-16">
        {items.map((item) => (
          <MediaCard key={item.id} item={item} mediaType={mediaType} isGridItem />
        ))}

        {loading &&
          Array.from({ length: 12 }).map((_, i) => (
            <div key={`skeleton-${i}`} className="aspect-video bg-gray-800 rounded animate-pulse" />
          ))}
      </div>

      {items.length === 0 && !loading && (
        <div className="text-center text-gray-400 py-20 px-4">
          <p className="text-lg">No content found</p>
          <p className="text-sm mt-1">Try a different filter or search term</p>
        </div>
      )}

      {sentinelRef && (
        <div ref={sentinelRef} className="h-10" />
      )}
    </div>
  )
}
