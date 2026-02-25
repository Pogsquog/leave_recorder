import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { supabase } from './supabase.js'
import Login from './pages/Login.jsx'
import Calendar from './pages/Calendar.jsx'
import Preferences from './pages/Preferences.jsx'

function Nav({ user, onLogout }) {
  return (
    <nav className="bg-gray-900/80 backdrop-blur-xl border-b border-cyan-500/20 sticky top-0 z-40">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-14 items-center">
          <div className="flex items-center gap-6">
            <span className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-fuchsia-400 tracking-wider">
              HOLIDAY HOLLIDAY
            </span>
            <div className="flex gap-4">
              <NavLink
                to="/"
                className={({ isActive }) =>
                  `text-sm transition-colors ${isActive ? 'text-cyan-300' : 'text-gray-400 hover:text-cyan-300'}`
                }
              >
                Calendar
              </NavLink>
              <NavLink
                to="/preferences"
                className={({ isActive }) =>
                  `text-sm transition-colors ${isActive ? 'text-cyan-300' : 'text-gray-400 hover:text-cyan-300'}`
                }
              >
                Settings
              </NavLink>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-500 hidden sm:block">{user?.email}</span>
            <button
              onClick={onLogout}
              className="text-xs text-gray-400 hover:text-fuchsia-400 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })

    return () => subscription.unsubscribe()
  }, [])

  const handleLogout = async () => {
    await supabase.auth.signOut()
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-cyan-400 animate-pulse">Loading…</div>
      </div>
    )
  }

  if (!session) {
    return <Login onLogin={() => { }} />
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <Nav user={session.user} onLogout={handleLogout} />
        <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Routes>
            <Route path="/" element={<Calendar user={session.user} />} />
            <Route path="/preferences" element={<Preferences />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
