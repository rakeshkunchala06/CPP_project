import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LogIn, MapPin, Sparkles } from 'lucide-react'
import api, { setToken, setUser } from '../api'

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const useDemo = () => {
    setEmail('demo@rakesh.com')
    setPassword('demo1234')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.login({ email, password })
      setToken(data.token)
      setUser(data.user)
      onLogin(data.user)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-12">
      <div className="text-center mb-8">
        <MapPin className="h-12 w-12 text-blue-600 mx-auto mb-3" />
        <h1 className="text-2xl font-bold text-gray-900">Welcome Back</h1>
        <p className="text-sm text-gray-500 mt-1">Sign in to TransitAccess</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <button
          type="button"
          onClick={useDemo}
          className="w-full mb-4 flex items-center justify-between gap-2 px-4 py-2.5 rounded-lg border border-dashed border-blue-300 bg-blue-50 hover:bg-blue-100 transition-colors text-left"
        >
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-blue-600 shrink-0" />
            <div>
              <div className="text-xs font-semibold text-blue-700 leading-tight">Try the Demo Account</div>
              <div className="text-[11px] text-gray-500 leading-tight">demo@rakesh.com &middot; demo1234</div>
            </div>
          </div>
          <span className="text-[10px] uppercase tracking-wider font-semibold text-blue-600">Use</span>
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 h-px bg-gray-200"></div>
          <span className="text-[10px] uppercase tracking-wider text-gray-400 font-medium">or sign in</span>
          <div className="flex-1 h-px bg-gray-200"></div>
        </div>

        {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="you@example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your password" />
          </div>
          <button type="submit" disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            <LogIn className="h-4 w-4" />
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-600 hover:underline font-medium">Register</Link>
        </p>
      </div>
    </div>
  )
}
