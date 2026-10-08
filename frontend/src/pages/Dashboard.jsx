import { useEffect, useState } from 'react'
import { api } from '../api'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import StatCard from '../components/StatCard'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [distribution, setDistribution] = useState([])

  useEffect(() => {
    Promise.all([
      api.get('/api/dashboard/summary'),
      api.get('/api/dashboard/risk-distribution')
    ]).then(([s, d]) => {
      setSummary(s.data)
      setDistribution(d.data)
    })
  }, [])

  if (!summary) return <div className="loading">Loading dashboard...</div>

  return (
    <div className="page">
      <div className="page-header">
        <div><div className="eyebrow">Operations</div><h1>Claims Dashboard</h1><p>Monitor claim volume, risk exposure and investigation workload.</p></div>
      </div>
      <div className="stats-grid">
        <StatCard label="Total Claims" value={summary.total_claims} hint="All submitted claims" />
        <StatCard label="High Risk" value={summary.high_risk_claims} hint="Requires attention" />
        <StatCard label="Investigations" value={summary.investigations} hint="Manual review queue" />
        <StatCard label="Approved" value={summary.approved_claims} hint="Approved or paid" />
      </div>
      <div className="content-grid">
        <section className="panel">
          <div className="panel-title">Risk distribution</div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={distribution} dataKey="count" nameKey="risk_level" innerRadius={70} outerRadius={105} paddingAngle={3}>
                  {distribution.map((_, i) => <Cell key={i} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="metric-row"><span>Average risk score</span><strong>{summary.average_risk_score}/100</strong></div>
          <div className="metric-row"><span>Total claim exposure</span><strong>₹{summary.total_claim_amount.toLocaleString()}</strong></div>
        </section>
        <section className="panel">
          <div className="panel-title">Decision engine</div>
          <div className="workflow">
            <div><span>1</span><p>Claim submitted</p></div>
            <div><span>2</span><p>Validation & policy checks</p></div>
            <div><span>3</span><p>Fraud + anomaly scoring</p></div>
            <div><span>4</span><p>Auto-approve or investigate</p></div>
            <div><span>5</span><p>Human decision and audit</p></div>
          </div>
          <div className="callout">
            <div className="callout-title">Responsible AI</div>
            <p>Risk scores support human decision-making. Flagged claims remain reviewable by investigators and every decision is audit logged.</p>
          </div>
        </section>
      </div>
    </div>
  )
}
