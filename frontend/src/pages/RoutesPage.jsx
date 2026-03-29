import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Map, Plus, Trash2, ChevronRight, Star } from 'lucide-react'
import api, { getToken } from '../api'

const TRANSIT_TYPES = ['bus', 'train', 'tram', 'metro']

function RatingStars({ rating }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <Star key={i} className={`h-4 w-4 ${i <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />
      ))}
      <span className="text-xs text-gray-500 ml-1">{rating}/5</span>
    </div>
  )
}

export default function RoutesPage() {
  const [routes, setRoutes] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', origin: '', destination: '', transitType: 'bus', accessibilityRating: 3, stops: [] })
  const [error, setError] = useState('')
  const isLoggedIn = !!getToken()

  useEffect(() => { loadRoutes() }, [])

  const loadRoutes = async () => {
    try {
      const data = await api.getRoutes()
      setRoutes(data.routes || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.createRoute(form)
      setShowForm(false)
      setForm({ name: '', origin: '', destination: '', transitType: 'bus', accessibilityRating: 3, stops: [] })
      loadRoutes()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this route?')) return
    try {
      await api.deleteRoute(id)
      loadRoutes()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-8 w-32"></div>
        {[1, 2, 3].map(i => <div key={i} className="skeleton h-28 rounded-xl"></div>)}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Map className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Routes</h1>
          <span className="text-sm text-gray-500">({routes.length})</span>
        </div>
        {isLoggedIn && (
          <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Add Route
          </button>
        )}
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">New Route</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Route Name *</label>
              <input type="text" required value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Transit Type</label>
              <select value={form.transitType} onChange={e => setForm({...form, transitType: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                {TRANSIT_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Origin *</label>
              <input type="text" required value={form.origin} onChange={e => setForm({...form, origin: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Destination *</label>
              <input type="text" required value={form.destination} onChange={e => setForm({...form, destination: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Accessibility Rating</label>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map(i => (
                <button key={i} type="button" onClick={() => setForm({...form, accessibilityRating: i})}
                  className="p-1">
                  <Star className={`h-6 w-6 ${i <= form.accessibilityRating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-3">
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">Create Route</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">Cancel</button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {routes.length === 0 ? (
          <div className="col-span-full bg-white rounded-xl border border-gray-200 p-12 text-center">
            <Map className="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No routes yet. Create your first route.</p>
          </div>
        ) : (
          routes.map(route => (
            <div key={route.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-blue-200 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <Link to={`/routes/${route.id}`} className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 capitalize">{route.name}</h3>
                </Link>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium">{route.transitType}</span>
                  {isLoggedIn && (
                    <button onClick={() => handleDelete(route.id)} className="p-1.5 text-gray-400 hover:text-red-500 rounded hover:bg-red-50">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                <span>{route.origin}</span>
                <span className="text-gray-400">&rarr;</span>
                <span>{route.destination}</span>
              </div>
              <div className="flex items-center justify-between">
                <RatingStars rating={route.accessibilityRating || 0} />
                <Link to={`/routes/${route.id}`} className="text-blue-600 text-sm font-medium hover:underline flex items-center gap-1">
                  Details <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
