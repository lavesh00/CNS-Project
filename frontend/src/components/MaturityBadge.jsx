export default function MaturityBadge({ adult, voteAverage, className = '' }) {
  let badge = 'TV-14'
  if (adult) {
    badge = 'R'
  } else if (voteAverage) {
    const v = Math.round(voteAverage)
    if (v >= 8) badge = 'PG-13'
    else if (v >= 6) badge = 'TV-14'
    else badge = 'TV-MA'
  }

  return (
    <span className={`maturity-badge ${className}`}>
      {badge}
    </span>
  )
}
