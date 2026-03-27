import { useState, useEffect } from 'react'
import { LayoutDashboard, MapPin, Map, Accessibility, Search, TrendingUp } from 'lucide-react'
import api from '../api'

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center gap-3">
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const data = await api.getDashboard()
      setStats(data)
    } catch (err) {
      setError(err.message)
      setStats({ totalStops: 0, totalRoutes: 0, accessibleStopsPct: 0, recentSearches: [] })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="skeleton h-8 w-48"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="skeleton h-28 rounded-xl"></div>)}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <LayoutDashboard className="h-8 w-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      </div>

      {error && <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg text-sm">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={MapPin} label="Total Stops" value={stats?.totalStops || 0} color="bg-blue-600" />
        <StatCard icon={Map} label="Total Routes" value={stats?.totalRoutes || 0} color="bg-green-600" />
        <StatCard icon={Accessibility} label="Accessible Stops" value={`${stats?.accessibleStopsPct || 0}%`} color="bg-purple-600" />
        <StatCard icon={TrendingUp} label="Recent Searches" value={stats?.recentSearches?.length || 0} color="bg-orange-500" />
      </div>

      {/* Accessibility Progress */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Accessibility Coverage</h2>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-green-500 h-4 rounded-full transition-all duration-500"
            style={{ width: `${stats?.accessibleStopsPct || 0}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-500 mt-2">{stats?.accessibleStopsPct || 0}% of stops have 3 or more accessibility features</p>
      </div>

      {/* Recent Searches */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Searches</h2>
        {stats?.recentSearches?.length > 0 ? (
          <div className="space-y-3">
            {stats.recentSearches.map((s, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <Search className="h-4 w-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{s.origin} &rarr; {s.destination}</p>
                  <p className="text-xs text-gray-500">{s.resultCount} results found</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No recent searches</p>
        )}
      </div>
    </div>
  )
}
