import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

const initial = {
  policy_number: 'POL-10001', customer_name: 'Aarav Mehta', policy_type: 'AUTO', location: 'Bengaluru',
  claim_type: 'COLLISION', claim_amount: 12500, previous_claims: 0, claim_frequency_30d: 0,
  location_risk: 0.15, mismatch_score: 0.10, late_report_days: 1, weekend_claim: false
}

export default function NewClaim() {
  const [form, setForm] = useState(initial)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const navigate = useNavigate()

  function update(k, v) { setForm(f => ({ ...f, [k]: v })) }

  async function submit(e) {
    e.preventDefault()
    setSaving(true); setError('')
    const payload = {
      ...form,
      claim_amount: Number(form.claim_amount), previous_claims: Number(form.previous_claims),
      claim_frequency_30d: Number(form.claim_frequency_30d), location_risk: Number(form.location_risk),
      mismatch_score: Number(form.mismatch_score), late_report_days: Number(form.late_report_days),
    }
    try {
      const { data } = await api.post('/api/claims', payload)
      navigate(`/claims/${data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create claim')
    } finally { setSaving(false) }
  }

  return (
    <div className="page">
      <div className="page-header"><div><div className="eyebrow">Claims</div><h1>Submit Claim</h1><p>Enter claim and behavioral signals for automated risk scoring.</p></div></div>
      <form className="panel form-panel" onSubmit={submit}>
        <div className="form-grid">
          <label>Policy number<input value={form.policy_number} onChange={e => update('policy_number', e.target.value)} /></label>
          <label>Customer name<input value={form.customer_name} onChange={e => update('customer_name', e.target.value)} /></label>
          <label>Policy type<select value={form.policy_type} onChange={e => update('policy_type', e.target.value)}><option>AUTO</option><option>HOME</option><option>PROPERTY</option><option>LIABILITY</option></select></label>
          <label>Location<input value={form.location} onChange={e => update('location', e.target.value)} /></label>
          <label>Claim type<select value={form.claim_type} onChange={e => update('claim_type', e.target.value)}><option>COLLISION</option><option>THEFT</option><option>WATER_DAMAGE</option><option>FIRE</option><option>LIABILITY</option></select></label>
          <label>Claim amount<input type="number" min="1" value={form.claim_amount} onChange={e => update('claim_amount', e.target.value)} /></label>
          <label>Previous claims<input type="number" min="0" value={form.previous_claims} onChange={e => update('previous_claims', e.target.value)} /></label>
          <label>Claims in last 30 days<input type="number" min="0" value={form.claim_frequency_30d} onChange={e => update('claim_frequency_30d', e.target.value)} /></label>
          <label>Location risk (0-1)<input type="number" min="0" max="1" step="0.01" value={form.location_risk} onChange={e => update('location_risk', e.target.value)} /></label>
          <label>Policy/claim mismatch (0-1)<input type="number" min="0" max="1" step="0.01" value={form.mismatch_score} onChange={e => update('mismatch_score', e.target.value)} /></label>
          <label>Late report days<input type="number" min="0" value={form.late_report_days} onChange={e => update('late_report_days', e.target.value)} /></label>
          <label className="checkbox-label"><input type="checkbox" checked={form.weekend_claim} onChange={e => update('weekend_claim', e.target.checked)} /> Weekend claim</label>
        </div>
        {error && <div className="error">{error}</div>}
        <div className="form-actions"><button className="primary-btn" disabled={saving}>{saving ? 'Scoring...' : 'Submit & Score Claim'}</button></div>
      </form>
    </div>
  )
}
