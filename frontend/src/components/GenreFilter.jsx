export default function GenreFilter({ genres, selectedGenre, onSelect }) {
  return (
    <div className="flex gap-2 overflow-x-auto hide-scrollbar px-3 sm:px-6 md:px-12 3xl:px-16 py-3 sm:py-4">
      {/* All button */}
      <button
        onClick={() => onSelect(null)}
        className={`flex-shrink-0 px-4 py-1.5 rounded-full text-xs sm:text-sm font-semibold transition-all duration-200 ${
          !selectedGenre
            ? 'bg-[#e50914] text-white shadow-md shadow-red-900/30'
            : 'bg-[#2f2f2f] text-gray-300 hover:bg-[#404040] border border-gray-700/50'
        }`}
      >
        All
      </button>
      {genres.map((genre) => (
        <button
          key={genre.id}
          onClick={() => onSelect(genre.id === selectedGenre ? null : genre.id)}
          className={`flex-shrink-0 px-4 py-1.5 rounded-full text-xs sm:text-sm font-semibold transition-all duration-200 ${
            genre.id === selectedGenre
              ? 'bg-[#e50914] text-white shadow-md shadow-red-900/30'
              : 'bg-[#2f2f2f] text-gray-300 hover:bg-[#404040] border border-gray-700/50'
          }`}
        >
          {genre.name}
        </button>
      ))}
    </div>
  )
}
