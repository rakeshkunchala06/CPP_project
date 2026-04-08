import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Heart, Trash2, Star, Map } from 'lucide-react'
import api, { getToken } from '../api'

export default function Favorites() {
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const isLoggedIn = !!getToken()

  useEffect(() => { loadFavorites() }, [])

  const loadFavorites = async () => {
    if (!isLoggedIn) {
      setLoading(false)
      return
    }
    try {
      const data = await api.getFavorites()
      setFavorites(data.favorites || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (favId) => {
    if (!confirm('Remove from favorites?')) return
    try {
      await api.removeFavorite(favId)
      loadFavorites()
    } catch (err) {
      setError(err.message)
    }
  }

  if (!isLoggedIn) {
    return (
      <div className="text-center py-16">
        <Heart className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Favorites</h2>
        <p className="text-gray-500 mb-4">Please log in to view your favorite routes.</p>
        <Link to="/login" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">Log In</Link>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-8 w-40"></div>
        {[1, 2].map(i => <div key={i} className="skeleton h-28 rounded-xl"></div>)}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Heart className="h-8 w-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">Favorites</h1>
        <span className="text-sm text-gray-500">({favorites.length})</span>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      {favorites.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Heart className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 mb-2">No favorite routes yet.</p>
          <Link to="/search" className="text-blue-600 hover:underline text-sm">Search for routes to save</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {favorites.map(fav => {
            const route = fav.route || {}
            return (
              <div key={fav.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-blue-200 transition-colors">
                <div className="flex items-start justify-between">
                  <Link to={`/routes/${fav.routeId}`} className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Map className="h-5 w-5 text-blue-600" />
                      <h3 className="text-lg font-semibold text-gray-900">{route.name || fav.routeId}</h3>
                      {route.transitType && (
                        <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium">{route.transitType}</span>
                      )}
                    </div>
                    {route.origin && (
                      <p className="text-sm text-gray-600 mb-2">{route.origin} &rarr; {route.destination}</p>
                    )}
                    {route.accessibilityRating && (
                      <div className="flex items-center gap-0.5">
                        {[1, 2, 3, 4, 5].map(i => (
                          <Star key={i} className={`h-4 w-4 ${i <= route.accessibilityRating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />
                        ))}
                      </div>
                    )}
                  </Link>
                  <button onClick={() => handleRemove(fav.id)}
                    className="p-2 text-gray-400 hover:text-red-500 rounded-lg hover:bg-red-50">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-2">Added: {new Date(fav.createdAt).toLocaleDateString()}</p>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
