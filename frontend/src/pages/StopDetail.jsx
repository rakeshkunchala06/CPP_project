import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { MapPin, ArrowLeft, Save, Trash2 } from 'lucide-react'
import api, { getToken } from '../api'

const ALL_FEATURES = [
  'wheelchair_ramp', 'elevator', 'tactile_paving',
  'audio_announcements', 'low_floor_boarding', 'accessible_toilet'
]

const TRANSIT_TYPES = ['bus', 'train', 'tram', 'metro']

export default function StopDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [stop, setStop] = useState(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const isLoggedIn = !!getToken()

  useEffect(() => { loadStop() }, [id])

  const loadStop = async () => {
    try {
      const data = await api.getStop(id)
      setStop(data.stop)
      setForm(data.stop)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setError('')
    setSuccess('')
    try {
      await api.updateStop(id, {
        name: form.name,
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        address: form.address,
        accessibilityFeatures: form.accessibilityFeatures,
        transitTypes: form.transitTypes,
      })
      setSuccess('Stop updated successfully')
      setEditing(false)
      loadStop()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this stop permanently?')) return
    try {
      await api.deleteStop(id)
      navigate('/stops')
    } catch (err) {
      setError(err.message)
    }
  }

  const toggleFeature = (f) => {
    setForm(prev => ({
      ...prev,
      accessibilityFeatures: prev.accessibilityFeatures?.includes(f)
        ? prev.accessibilityFeatures.filter(x => x !== f)
        : [...(prev.accessibilityFeatures || []), f]
    }))
  }

  const toggleTransit = (t) => {
    setForm(prev => ({
      ...prev,
      transitTypes: prev.transitTypes?.includes(t)
        ? prev.transitTypes.filter(x => x !== t)
        : [...(prev.transitTypes || []), t]
    }))
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-8 w-48"></div>
        <div className="skeleton h-64 rounded-xl"></div>
      </div>
    )
  }

  if (!stop) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Stop not found</p>
        <Link to="/stops" className="text-blue-600 hover:underline text-sm mt-2 inline-block">Back to Stops</Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/stops" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </Link>
        <MapPin className="h-8 w-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">{editing ? 'Edit Stop' : stop.name}</h1>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}
      {success && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">{success}</div>}

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            {editing ? (
              <input type="text" value={form.name || ''} onChange={e => setForm({...form, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            ) : (
              <p className="text-gray-900">{stop.name}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
            {editing ? (
              <input type="text" value={form.address || ''} onChange={e => setForm({...form, address: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            ) : (
              <p className="text-gray-900">{stop.address || 'N/A'}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
            {editing ? (
              <input type="number" step="any" value={form.latitude || ''} onChange={e => setForm({...form, latitude: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            ) : (
              <p className="text-gray-900">{stop.latitude}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
            {editing ? (
              <input type="number" step="any" value={form.longitude || ''} onChange={e => setForm({...form, longitude: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            ) : (
              <p className="text-gray-900">{stop.longitude}</p>
            )}
          </div>
        </div>

        {/* Transit Types */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Transit Types</label>
          <div className="flex flex-wrap gap-2">
            {TRANSIT_TYPES.map(t => {
              const active = (editing ? form.transitTypes : stop.transitTypes)?.includes(t)
              return (
                <button key={t} type="button"
                  onClick={() => editing && toggleTransit(t)}
                  disabled={!editing}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium border ${
                    active ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-500 border-gray-300'
                  } ${editing ? 'cursor-pointer hover:opacity-80' : 'cursor-default'}`}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </button>
              )
            })}
          </div>
        </div>

        {/* Accessibility Features */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Accessibility Features</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {ALL_FEATURES.map(f => {
              const active = (editing ? form.accessibilityFeatures : stop.accessibilityFeatures)?.includes(f)
              const label = f.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
              return (
                <label key={f} className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                  active ? 'bg-green-50 border-green-300' : 'bg-gray-50 border-gray-200'
                } ${editing ? 'hover:border-green-400' : ''}`}>
                  <input
                    type="checkbox"
                    checked={active || false}
                    onChange={() => editing && toggleFeature(f)}
                    disabled={!editing}
                    className="h-4 w-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                  />
                  <span className={`text-sm font-medium ${active ? 'text-green-800' : 'text-gray-500'}`}>{label}</span>
                </label>
              )
            })}
          </div>
        </div>

        {isLoggedIn && (
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            {editing ? (
              <>
                <button onClick={handleSave} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
                  <Save className="h-4 w-4" /> Save Changes
                </button>
                <button onClick={() => { setEditing(false); setForm(stop); }} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">Cancel</button>
              </>
            ) : (
              <>
                <button onClick={() => setEditing(true)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">Edit Stop</button>
                <button onClick={handleDelete} className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100">
                  <Trash2 className="h-4 w-4" /> Delete
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
