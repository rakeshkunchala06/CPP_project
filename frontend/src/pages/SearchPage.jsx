import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Star, Filter, MapPin } from 'lucide-react'
import api from '../api'

const ALL_FEATURES = [
  'wheelchair_ramp', 'elevator', 'tactile_paving',
  'audio_announcements', 'low_floor_boarding', 'accessible_toilet'
]

export default function SearchPage() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [needs, setNeeds] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const toggleNeed = (n) => {
    setNeeds(prev => prev.includes(n) ? prev.filter(x => x !== n) : [...prev, n])
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.search({ origin, destination, accessibilityNeeds: needs })
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Search className="h-8 w-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">Search Routes</h1>
      </div>

      <form onSubmit={handleSearch} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Origin *</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              <input type="text" required value={origin} onChange={e => setOrigin(e.target.value)}
                placeholder="Starting point..."
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Destination *</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              <input type="text" required value={destination} onChange={e => setDestination(e.target.value)}
                placeholder="Where to..."
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
          </div>
        </div>

        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Filter className="h-4 w-4" /> Accessibility Requirements
          </label>
          <div className="flex flex-wrap gap-2">
            {ALL_FEATURES.map(f => (
              <button key={f} type="button" onClick={() => toggleNeed(f)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                  needs.includes(f) ? 'bg-green-600 text-white border-green-600' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                }`}>
                {f.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
              </button>
            ))}
          </div>
        </div>

        <button type="submit" disabled={loading}
          className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
          <Search className="h-4 w-4" />
          {loading ? 'Searching...' : 'Search Routes'}
        </button>
      </form>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      {results && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Results ({results.count || 0})
            </h2>
            {results.search && (
              <p className="text-sm text-gray-500">
                {results.search.origin} &rarr; {results.search.destination}
              </p>
            )}
          </div>

          {results.results?.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
              <Search className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No matching routes found. Try adjusting your search criteria.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {results.results?.map(route => (
                <Link key={route.routeId} to={`/routes/${route.routeId}`}
                  className="block bg-white rounded-xl border border-gray-200 p-5 hover:border-blue-200 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{route.name}</h3>
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium">{route.transitType}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                    <span>{route.origin}</span>
                    <span className="text-gray-400">&rarr;</span>
                    <span>{route.destination}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map(i => (
                      <Star key={i} className={`h-4 w-4 ${i <= route.accessibilityRating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />
                    ))}
                    <span className="text-xs text-gray-500 ml-1">Accessibility: {route.accessibilityRating}/5</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
