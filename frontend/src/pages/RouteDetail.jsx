import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { Map, ArrowLeft, Star, Trash2, Save, MapPin, Plus, ChevronUp, ChevronDown, X } from 'lucide-react'
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
  const [allStops, setAllStops] = useState([])
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showAddStop, setShowAddStop] = useState(false)
  const isLoggedIn = !!getToken()

  useEffect(() => { loadRoute() }, [id])

  const loadRoute = async () => {
    try {
      const data = await api.getRoute(id)
      setRoute(data.route)
      setForm(data.route)
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

  const loadAllStops = async () => {
    try {
      const data = await api.getStops()
      setAllStops(data.stops || data || [])
    } catch { /* ignore */ }
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

  const handleAddStopToRoute = async (stopId) => {
    const currentStops = route.stops || []
    if (currentStops.includes(stopId)) {
      setError('Stop already on this route')
      return
    }
    const newStops = [...currentStops, stopId]
    try {
      await api.updateRoute(id, { stops: newStops })
      setSuccess('Stop added to route')
      setShowAddStop(false)
      loadRoute()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleRemoveStop = async (stopId) => {
    const newStops = (route.stops || []).filter(s => s !== stopId)
    try {
      await api.updateRoute(id, { stops: newStops })
      setSuccess('Stop removed from route')
      loadRoute()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleMoveStop = async (idx, direction) => {
    const stops = [...(route.stops || [])]
    const newIdx = idx + direction
    if (newIdx < 0 || newIdx >= stops.length) return
    ;[stops[idx], stops[newIdx]] = [stops[newIdx], stops[idx]]
    try {
      await api.updateRoute(id, { stops })
      loadRoute()
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

  const availableStops = allStops.filter(s => !(route.stops || []).includes(s.id))

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/routes" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </Link>
        <Map className="h-8 w-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900 capitalize">{route.name}</h1>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}<button onClick={() => setError('')} className="float-right text-red-400 hover:text-red-600 bg-transparent border-none cursor-pointer">x</button></div>}
      {success && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">{success}<button onClick={() => setSuccess('')} className="float-right text-green-400 hover:text-green-600 bg-transparent border-none cursor-pointer">x</button></div>}

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
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Stop Sequence</h2>
          <div className="flex items-center gap-2">
            {stopDetails.length > 0 && (
              <span className="text-xs text-gray-500">{stopDetails.length} stop{stopDetails.length !== 1 ? 's' : ''}</span>
            )}
            {isLoggedIn && (
              <button
                onClick={() => { setShowAddStop(!showAddStop); if (!showAddStop) loadAllStops(); }}
                className="flex items-center gap-1 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-100 border border-blue-200 cursor-pointer"
              >
                <Plus className="h-4 w-4" /> Add Stop
              </button>
            )}
          </div>
        </div>

        {/* Add Stop dropdown */}
        {showAddStop && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-gray-700">Select a stop to add</p>
              <button onClick={() => setShowAddStop(false)} className="text-gray-400 hover:text-gray-600 bg-transparent border-none cursor-pointer">
                <X className="h-4 w-4" />
              </button>
            </div>
            {availableStops.length === 0 ? (
              <p className="text-sm text-gray-500">No available stops. <Link to="/stops" className="text-blue-600 hover:underline">Create one first</Link>.</p>
            ) : (
              <div className="grid gap-2 max-h-48 overflow-y-auto">
                {availableStops.map(stop => (
                  <button
                    key={stop.id}
                    onClick={() => handleAddStopToRoute(stop.id)}
                    className="flex items-center gap-2 w-full text-left px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm hover:bg-blue-50 hover:border-blue-200 transition-colors cursor-pointer"
                  >
                    <MapPin className="h-4 w-4 text-gray-400 shrink-0" />
                    <span className="font-medium text-gray-900">{stop.name}</span>
                    {stop.accessibilityFeatures?.length > 0 && (
                      <span className="text-xs text-green-600 ml-auto">{stop.accessibilityFeatures.length} features</span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {(() => {
          const inaccessibleCount = stopDetails.filter(
            s => !s.accessibilityFeatures || s.accessibilityFeatures.length < 3
          ).length
          if (stopDetails.length > 0 && inaccessibleCount > 0) {
            return (
              <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-lg px-3 py-2 text-xs mb-4">
                {inaccessibleCount} stop{inaccessibleCount !== 1 ? 's' : ''} on this route may not be fully accessible.
              </div>
            )
          }
          if (stopDetails.length > 0) {
            return (
              <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg px-3 py-2 text-xs mb-4">
                All stops on this route meet the basic accessibility criteria.
              </div>
            )
          }
          return null
        })()}

        {stopDetails.length === 0 ? (
          <div className="text-center py-6">
            <MapPin className="h-10 w-10 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">No intermediate stops have been added to this route yet.</p>
            {isLoggedIn && (
              <button
                onClick={() => { setShowAddStop(true); loadAllStops(); }}
                className="mt-3 inline-flex items-center gap-1 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 cursor-pointer border-none"
              >
                <Plus className="h-4 w-4" /> Add First Stop
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {stopDetails.map((stop, idx) => {
              const features = stop.accessibilityFeatures || []
              const isFullyAccessible = features.length >= 3
              return (
                <div key={stop.id || idx} className="flex items-start gap-4">
                  <div className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                      isFullyAccessible ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'
                    }`}>
                      {idx + 1}
                    </div>
                    {idx < stopDetails.length - 1 && <div className="w-0.5 h-8 bg-blue-200 mt-1"></div>}
                  </div>
                  <div className="flex-1 pb-2">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-gray-400" />
                      <Link to={`/stops/${stop.id}`} className="font-medium text-gray-900 hover:text-blue-600">{stop.name}</Link>
                      {!isFullyAccessible && (
                        <span className="text-[10px] uppercase tracking-wide font-semibold text-red-500">Limited access</span>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {ALL_FEATURES.map(f => (
                        <span key={f} className={`text-xs px-2 py-0.5 rounded-full ${
                          features.includes(f) ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-400'
                        }`}>
                          {f.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                  {isLoggedIn && (
                    <div className="flex flex-col gap-1 shrink-0">
                      <button onClick={() => handleMoveStop(idx, -1)} disabled={idx === 0}
                        className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded disabled:opacity-30 bg-transparent border-none cursor-pointer" title="Move up">
                        <ChevronUp className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleMoveStop(idx, 1)} disabled={idx === stopDetails.length - 1}
                        className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded disabled:opacity-30 bg-transparent border-none cursor-pointer" title="Move down">
                        <ChevronDown className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleRemoveStop(stop.id)}
                        className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded bg-transparent border-none cursor-pointer" title="Remove stop">
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
