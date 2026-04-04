import { SERVERS } from '../utils/constants'

export default function ServerSelector({ currentServer, onServerChange }) {
  return (
    <div className="flex flex-wrap items-center gap-2 sm:gap-3 mt-3 sm:mt-4">
      <span className="text-gray-400 text-xs sm:text-sm">Server:</span>
      <div className="flex flex-wrap gap-1.5 sm:gap-2">
        {SERVERS.map((server) => (
          <button
            key={server}
            onClick={() => onServerChange(server)}
            className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded text-xs sm:text-sm font-medium transition ${
              server === currentServer
                ? 'bg-[#e50914] text-white'
                : 'bg-[#2f2f2f] text-gray-300 hover:bg-[#404040] active:bg-[#505050]'
            }`}
          >
            Server {server}
          </button>
        ))}
      </div>
    </div>
  )
}
