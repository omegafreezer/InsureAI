import { useEffect, useState } from 'react'
import { Navigate, Route, Routes, NavLink, useNavigate } from 'react-router-dom'
import { api, clearToken } from './api'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Claims from './pages/Claims'
import NewClaim from './pages/NewClaim'
import ClaimDetail from './pages/ClaimDetail'

function Protected({ children }) {
  return localStorage.getItem('insureai_token') ? children : <Navigate to="/login" replace />
}

export default function App() {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    if (localStorage.getItem('insureai_token')) {
      api.get('/api/auth/me').then(r => setUser(r.data)).catch(() => {
        clearToken()
        setUser(null)
      })
    }
  }, [])

  function logout() {
    clearToken()
    setUser(null)
    navigate('/login')
  }

  return (
    <div className="app-shell">
      {localStorage.getItem('insureai_token') && (
        <aside className="sidebar">
          <div className="brand">InsureAI</div>
          <div className="subtitle">Claims Intelligence</div>
          <nav>
            <NavLink to="/">Dashboard</NavLink>
            <NavLink to="/claims">Claims</NavLink>
            {user?.role !== 'INVESTIGATOR' && <NavLink to="/claims/new">New Claim</NavLink>}
          </nav>
          <div className="sidebar-footer">
            <div>{user?.full_name || 'User'}</div>
            <span>{user?.role || 'AUTHENTICATING'}</span>
            <button className="ghost-btn" onClick={logout}>Sign out</button>
          </div>
        </aside>
      )}
      <main className="main-content">
        <Routes>
          <Route path="/login" element={<Login onLogin={setUser} />} />
          <Route path="/" element={<Protected><Dashboard /></Protected>} />
          <Route path="/claims" element={<Protected><Claims /></Protected>} />
          <Route path="/claims/new" element={<Protected><NewClaim /></Protected>} />
          <Route path="/claims/:id" element={<Protected><ClaimDetail /></Protected>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
