import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api'
import StatusBadge from '../components/StatusBadge'

export default function ClaimDetail() {
  const { id } = useParams()
  const [claim, setClaim] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [note, setNote] = useState('')
  const [error, setError] = useState('')

  async function load() {
    const { data } = await api.get(`/api/claims/${id}`)
    setClaim(data)
  }

  useEffect(() => { load() }, [id])

  async function rescore() {
    try {
      const { data } = await api.post(`/api/claims/${id}/rescore`)
      setExplanation(data)
      load()
    } catch (e) { setError(e.response?.data?.detail || 'Rescore failed') }
  }

  async function decision(decision) {
    try {
      const { data } = await api.post(`/api/claims/${id}/decision`, { decision, note })
      setClaim(data)
      setNote('')
    } catch (e) { setError(e.response?.data?.detail || 'Decision failed') }
  }

  if (!claim) return <div className="loading">Loading claim...</div>

  return (
    <div className="page">
      <div className="page-header">
        <div><div className="eyebrow">Claim review</div><h1>{claim.claim_number}</h1><p>{claim.customer_name} · {claim.policy_type} · {claim.claim_type}</p></div>
        <StatusBadge value={claim.status} />
      </div>
      <div className="content-grid">
        <section className="panel">
          <div className="panel-title">Risk assessment</div>
          <div className="risk-score"><div className="score-number">{claim.risk_score?.toFixed(1)}</div><div>/100</div></div>
          <div className="risk-level">{claim.risk_level} RISK</div>
          <div className="metric-row"><span>Fraud probability</span><strong>{(claim.fraud_probability * 100).toFixed(1)}%</strong></div>
          <div className="metric-row"><span>Anomaly score</span><strong>{(claim.anomaly_score * 100).toFixed(1)}%</strong></div>
          <div className="metric-row"><span>Claim amount</span><strong>₹{claim.claim_amount.toLocaleString()}</strong></div>
          <button className="secondary-btn" onClick={rescore}>Re-score & Explain</button>
        </section>
        <section className="panel">
          <div className="panel-title">Claim information</div>
          <div className="detail-grid">
            <div><span>Policy</span><strong>{claim.policy_number}</strong></div>
            <div><span>Location</span><strong>{claim.location}</strong></div>
            <div><span>Claim type</span><strong>{claim.claim_type}</strong></div>
            <div><span>Decision</span><strong>{claim.decision_reason}</strong></div>
          </div>
          {claim.status === 'INVESTIGATION' && <>
            <div className="panel-title spaced">Investigator decision</div>
            <textarea placeholder="Investigation note" value={note} onChange={e => setNote(e.target.value)} />
            <div className="button-row"><button className="primary-btn" onClick={() => decision('APPROVE')}>Approve</button><button className="danger-btn" onClick={() => decision('REJECT')}>Reject</button></div>
          </>}
        </section>
      </div>
      {explanation && <section className="panel explanation-panel"><div className="panel-title">Explainable risk factors</div>{explanation.factors.map((f, i) => <div className="factor" key={i}><div><strong>{f.feature}</strong><span>{f.message}</span></div><span className="factor-impact">{f.impact > 0 ? '+' : ''}{f.impact}</span></div>)}</section>}
      {error && <div className="error">{error}</div>}
    </div>
  )
}
