import { useState } from 'react'
import { supabase } from '../supabase.js'

export default function Login({ onLogin }) {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(false)
    const [showRegister, setShowRegister] = useState(false)
    const [resetSent, setResetSent] = useState(false)

    const handleLogin = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) setError(error.message)
        else onLogin?.()
        setLoading(false)
    }

    const handleRegister = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        const { error } = await supabase.auth.signUp({ email, password })
        if (error) setError(error.message)
        else setError('Check your email to confirm your account.')
        setLoading(false)
    }

    const handleReset = async () => {
        if (!email) { setError('Enter your email address first.'); return }
        const { error } = await supabase.auth.resetPasswordForEmail(email)
        if (error) setError(error.message)
        else setResetSent(true)
    }

    return (
        <div className="min-h-screen flex items-center justify-center px-4">
            <div className="card-dark rounded-2xl p-8 w-full max-w-md neon-border">
                <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-fuchsia-400 tracking-wider mb-2 text-center">
                    HOLIDAY HOLLIDAY
                </h1>
                <p className="text-gray-400 text-sm text-center mb-8">Leave recorder</p>

                <div className="flex mb-6 rounded-lg overflow-hidden border border-cyan-500/30">
                    <button
                        className={`flex-1 py-2 text-sm font-medium transition-colors ${!showRegister ? 'bg-cyan-500/20 text-cyan-300' : 'text-gray-400 hover:text-cyan-300'}`}
                        onClick={() => setShowRegister(false)}
                    >
                        Sign In
                    </button>
                    <button
                        className={`flex-1 py-2 text-sm font-medium transition-colors ${showRegister ? 'bg-cyan-500/20 text-cyan-300' : 'text-gray-400 hover:text-cyan-300'}`}
                        onClick={() => setShowRegister(true)}
                    >
                        Register
                    </button>
                </div>

                <form onSubmit={showRegister ? handleRegister : handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-xs text-gray-400 mb-1">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            required
                            className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-cyan-100 text-sm focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400/50"
                            placeholder="you@example.com"
                        />
                    </div>
                    <div>
                        <label className="block text-xs text-gray-400 mb-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required
                            className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-cyan-100 text-sm focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400/50"
                            placeholder="••••••••"
                        />
                    </div>

                    {error && (
                        <div className={`text-xs p-3 rounded-lg border ${error.includes('Check') ? 'bg-green-900/30 border-green-500/50 text-green-400' : 'bg-red-900/30 border-red-500/50 text-red-400'}`}>
                            {error}
                        </div>
                    )}
                    {resetSent && <div className="text-xs p-3 rounded-lg border bg-green-900/30 border-green-500/50 text-green-400">Password reset email sent!</div>}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-cyan-500 to-fuchsia-500 text-white py-2.5 rounded-lg text-sm font-medium hover:from-cyan-400 hover:to-fuchsia-400 transition-all neon-button-cyan disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? '...' : showRegister ? 'Create Account' : 'Sign In'}
                    </button>
                </form>

                {!showRegister && (
                    <button
                        onClick={handleReset}
                        className="w-full text-center text-xs text-gray-500 hover:text-cyan-400 mt-4 transition-colors"
                    >
                        Forgot password?
                    </button>
                )}
            </div>
        </div>
    )
}
