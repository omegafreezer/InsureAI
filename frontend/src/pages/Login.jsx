import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setToken } from '../api'

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('Admin@123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function submit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post('/api/auth/login', { username, password })
      setToken(data.access_token)
      const me = await api.get('/api/auth/me')
      onLogin(me.data)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="brand">InsureAI</div>
        <p className="muted">Claims risk & fraud intelligence</p>
        <form onSubmit={submit}>
          <label>Username<input value={username} onChange={e => setUsername(e.target.value)} /></label>
          <label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} /></label>
          {error && <div className="error">{error}</div>}
          <button className="primary-btn" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'}</button>
        </form>
        <div className="demo-box">
          <div>Demo accounts</div>
          <small>admin / Admin@123</small>
          <small>agent / Agent@123</small>
          <small>investigator / Invest@123</small>
        </div>
      </div>
    </div>
  )
}
