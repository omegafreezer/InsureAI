export default function StatusBadge({ value }) {
  const normalized = String(value || '').toLowerCase().replaceAll('_', '-')
  return <span className={`badge badge-${normalized}`}>{value}</span>
}
