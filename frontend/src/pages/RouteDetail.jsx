import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { Map, ArrowLeft, Star, Trash2, Save, MapPin } from 'lucide-react'
import api, { getToken } from '../api'

const ALL_FEATURES = [
  'wheelchair_ramp', 'elevator', 'tactile_paving',
  'audio_announcements', 'low_floor_boarding', 'accessible_toilet'
]

export default function RouteDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [route, setRoute] = useState(null)
  const [stopDetails, setStopDetails] = useState([])
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const isLoggedIn = !!getToken()

  useEffect(() => { loadRoute() }, [id])

  const loadRoute = async () => {
    try {
      const data = await api.getRoute(id)
      setRoute(data.route)
      setForm(data.route)
      // Load stop details
      const stopIds = data.route.stops || []
      const details = []
      for (const sid of stopIds) {
        try {
          const sd = await api.getStop(sid)
          details.push(sd.stop)
        } catch {
          details.push({ id: sid, name: sid })
        }
      }
      setStopDetails(details)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setError('')
    try {
      await api.updateRoute(id, {
        name: form.name,
        origin: form.origin,
        destination: form.destination,
        transitType: form.transitType,
        accessibilityRating: form.accessibilityRating,
      })
      setSuccess('Route updated successfully')
      setEditing(false)
      loadRoute()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this route permanently?')) return
    try {
      await api.deleteRoute(id)
      navigate('/routes')
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-8 w-48"></div>
        <div className="skeleton h-64 rounded-xl"></div>
      </div>
    )
  }

  if (!route) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Route not found</p>
        <Link to="/routes" className="text-blue-600 hover:underline text-sm mt-2 inline-block">Back to Routes</Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/routes" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </Link>
        <Map className="h-8 w-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900 capitalize">{route.name}</h1>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}
      {success && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">{success}</div>}

      {/* Route Info */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Route Name</label>
            {editing ? (
              <input type="text" value={form.name || ''} onChange={e => setForm({...form, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            ) : (
              <p className="text-gray-900 font-medium">{route.name}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Transit Type</label>
            {editing ? (
              <select value={form.transitType || 'bus'} onChange={e => setForm({...form, transitType: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                {['bus', 'train', 'tram', 'metro'].map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
              </select>
            ) : (
              <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium">{route.transitType}</span>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Origin</label>
            {editing ? (
              <input type="text" value={form.origin || ''} onChange={e => setForm({...form, origin: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            ) : (
              <p className="text-gray-900">{route.origin}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Destination</label>
            {editing ? (
              <input type="text" value={form.destination || ''} onChange={e => setForm({...form, destination: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            ) : (
              <p className="text-gray-900">{route.destination}</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Accessibility Rating</label>
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map(i => (
              <button key={i} type="button"
                onClick={() => editing && setForm({...form, accessibilityRating: i})}
                disabled={!editing}
                className={editing ? 'p-1 cursor-pointer' : 'p-1 cursor-default'}>
                <Star className={`h-6 w-6 ${i <= (editing ? form.accessibilityRating : route.accessibilityRating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />
              </button>
            ))}
          </div>
        </div>

        {isLoggedIn && (
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            {editing ? (
              <>
                <button onClick={handleSave} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
                  <Save className="h-4 w-4" /> Save Changes
                </button>
                <button onClick={() => { setEditing(false); setForm(route); }} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">Cancel</button>
              </>
            ) : (
              <>
                <button onClick={() => setEditing(true)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">Edit Route</button>
                <button onClick={handleDelete} className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100">
                  <Trash2 className="h-4 w-4" /> Delete
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {/* Stop Sequence */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Stop Sequence</h2>
        {stopDetails.length === 0 ? (
          <p className="text-sm text-gray-500">No intermediate stops on this route.</p>
        ) : (
          <div className="space-y-3">
            {stopDetails.map((stop, idx) => (
              <div key={stop.id || idx} className="flex items-start gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold">{idx + 1}</div>
                  {idx < stopDetails.length - 1 && <div className="w-0.5 h-8 bg-blue-200 mt-1"></div>}
                </div>
                <div className="flex-1 pb-2">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-gray-400" />
                    <Link to={`/stops/${stop.id}`} className="font-medium text-gray-900 hover:text-blue-600">{stop.name}</Link>
                  </div>
                  {stop.accessibilityFeatures && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {ALL_FEATURES.map(f => (
                        <span key={f} className={`text-xs px-2 py-0.5 rounded-full ${
                          stop.accessibilityFeatures.includes(f) ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-400'
                        }`}>
                          {f.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
