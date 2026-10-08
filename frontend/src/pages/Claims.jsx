import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import StatusBadge from '../components/StatusBadge'

export default function Claims() {
  const [claims, setClaims] = useState([])
  const [risk, setRisk] = useState('')
  const [status, setStatus] = useState('')

  async function load() {
    const params = {}
    if (risk) params.risk = risk
    if (status) params.status = status
    const { data } = await api.get('/api/claims', { params })
    setClaims(data)
  }

  useEffect(() => { load() }, [risk, status])

  return (
    <div className="page">
      <div className="page-header">
        <div><div className="eyebrow">Operations</div><h1>Claims</h1><p>Review claim status, risk scores and investigation routing.</p></div>
        <Link className="primary-btn link-btn" to="/claims/new">New Claim</Link>
      </div>
      <div className="filters panel">
        <select value={risk} onChange={e => setRisk(e.target.value)}><option value="">All risk levels</option><option>LOW</option><option>MEDIUM</option><option>HIGH</option></select>
        <select value={status} onChange={e => setStatus(e.target.value)}><option value="">All statuses</option><option>SUBMITTED</option><option>INVESTIGATION</option><option>AUTO_APPROVED</option><option>APPROVED</option><option>REJECTED</option><option>PAID</option></select>
      </div>
      <div className="panel table-panel">
        <table>
          <thead><tr><th>Claim</th><th>Customer</th><th>Type</th><th>Amount</th><th>Risk</th><th>Status</th><th></th></tr></thead>
          <tbody>
            {claims.map(c => (
              <tr key={c.id}>
                <td><Link to={`/claims/${c.id}`} className="table-link">{c.claim_number}</Link></td>
                <td>{c.customer_name}</td>
                <td>{c.claim_type}</td>
                <td>₹{c.claim_amount.toLocaleString()}</td>
                <td>{c.risk_score?.toFixed(1)}/100</td>
                <td><StatusBadge value={c.status} /></td>
                <td><Link to={`/claims/${c.id}`} className="table-link">Review</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
