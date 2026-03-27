import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { MapPin, Plus, Trash2, ChevronRight } from 'lucide-react'
import api from '../api'
import { getToken } from '../api'

const ALL_FEATURES = [
  'wheelchair_ramp', 'elevator', 'tactile_paving',
  'audio_announcements', 'low_floor_boarding', 'accessible_toilet'
]

const TRANSIT_TYPES = ['bus', 'train', 'tram', 'metro']

function FeatureBadge({ feature, available }) {
  const label = feature.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
      available ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-500'
    }`}>
      {label}
    </span>
  )
}

export default function Stops() {
  const [stops, setStops] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', latitude: '', longitude: '', address: '', accessibilityFeatures: [], transitTypes: [] })
  const [error, setError] = useState('')
  const isLoggedIn = !!getToken()

  useEffect(() => { loadStops() }, [])

  const loadStops = async () => {
    try {
      const data = await api.getStops()
      setStops(data.stops || [])
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
      await api.createStop({
        ...form,
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
      })
      setShowForm(false)
      setForm({ name: '', latitude: '', longitude: '', address: '', accessibilityFeatures: [], transitTypes: [] })
      loadStops()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this stop?')) return
    try {
      await api.deleteStop(id)
      loadStops()
    } catch (err) {
      setError(err.message)
    }
  }

  const toggleFeature = (f) => {
    setForm(prev => ({
      ...prev,
      accessibilityFeatures: prev.accessibilityFeatures.includes(f)
        ? prev.accessibilityFeatures.filter(x => x !== f)
        : [...prev.accessibilityFeatures, f]
    }))
  }

  const toggleTransit = (t) => {
    setForm(prev => ({
      ...prev,
      transitTypes: prev.transitTypes.includes(t)
        ? prev.transitTypes.filter(x => x !== t)
        : [...prev.transitTypes, t]
    }))
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-8 w-32"></div>
        {[1, 2, 3].map(i => <div key={i} className="skeleton h-24 rounded-xl"></div>)}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <MapPin className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Stops</h1>
          <span className="text-sm text-gray-500">({stops.length})</span>
        </div>
        {isLoggedIn && (
          <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Add Stop
          </button>
        )}
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">New Stop</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input type="text" required value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
              <input type="text" value={form.address} onChange={e => setForm({...form, address: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Latitude *</label>
              <input type="number" step="any" required value={form.latitude} onChange={e => setForm({...form, latitude: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Longitude *</label>
              <input type="number" step="any" required value={form.longitude} onChange={e => setForm({...form, longitude: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Transit Types</label>
            <div className="flex flex-wrap gap-2">
              {TRANSIT_TYPES.map(t => (
                <button key={t} type="button" onClick={() => toggleTransit(t)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium border ${
                    form.transitTypes.includes(t) ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                  }`}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Accessibility Features</label>
            <div className="flex flex-wrap gap-2">
              {ALL_FEATURES.map(f => (
                <button key={f} type="button" onClick={() => toggleFeature(f)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium border ${
                    form.accessibilityFeatures.includes(f) ? 'bg-green-600 text-white border-green-600' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                  }`}>
                  {f.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-3">
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">Create Stop</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">Cancel</button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {stops.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <MapPin className="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No stops yet. Add your first stop.</p>
          </div>
        ) : (
          stops.map(stop => (
            <div key={stop.stopId} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-blue-200 transition-colors">
              <div className="flex items-start justify-between">
                <Link to={`/stops/${stop.stopId}`} className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{stop.name}</h3>
                    {stop.transitTypes?.map(t => (
                      <span key={t} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium">{t}</span>
                    ))}
                  </div>
                  {stop.address && <p className="text-sm text-gray-500 mb-3">{stop.address}</p>}
                  <div className="flex flex-wrap gap-1.5">
                    {ALL_FEATURES.map(f => (
                      <FeatureBadge key={f} feature={f} available={stop.accessibilityFeatures?.includes(f)} />
                    ))}
                  </div>
                </Link>
                <div className="flex items-center gap-2 ml-4">
                  {isLoggedIn && (
                    <button onClick={() => handleDelete(stop.stopId)} className="p-2 text-gray-400 hover:text-red-500 rounded-lg hover:bg-red-50">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                  <Link to={`/stops/${stop.stopId}`} className="p-2 text-gray-400 hover:text-blue-600">
                    <ChevronRight className="h-5 w-5" />
                  </Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
