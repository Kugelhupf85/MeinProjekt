import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Globe, MapPin, Users } from 'lucide-react';

const WorldList = () => {
  const [worlds, setWorlds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWorlds();
  }, []);

  const fetchWorlds = async () => {
    try {
      setLoading(true);
      // For now, we'll use mock data since authentication is required
      const mockWorlds = [
        {
          entity_id: 'WLD-123456789012',
          name: 'Mittelerde',
          description: 'Eine epische Fantasy-Welt voller Magie und Abenteuer...',
          general_mood: 'Episch und mystisch',
          pill: {
            region_count: 5,
            total_locations: 23,
            key_religions: ['Valar-Verehrung', 'Naturgeister'],
            primary_languages: ['Sindarin', 'Westron'],
            magic_system_type: 'Göttliche Magie'
          },
          created_at: '2025-06-08T00:00:00Z'
        },
        {
          entity_id: 'WLD-234567890123',
          name: 'Drachenlande',
          description: 'Ein Reich der Drachen und mutigen Helden...',
          general_mood: 'Gefährlich und aufregend',
          pill: {
            region_count: 3,
            total_locations: 15,
            key_religions: ['Drachenkult', 'Kriegsgötter'],
            primary_languages: ['Drakonisch', 'Gemeinsprache'],
            magic_system_type: 'Elementarmagie'
          },
          created_at: '2025-06-07T00:00:00Z'
        }
      ];
      
      setWorlds(mockWorlds);
      setError(null);
    } catch (err) {
      setError('Fehler beim Laden der Welten: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Welten</h1>
          <p className="text-gray-600 mt-1">Verwalte deine Fantasy-Welten und ihre Regionen</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
          <Plus size={20} />
          Neue Welt
        </button>
      </div>

      {/* World Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {worlds.map((world) => (
          <Link
            key={world.entity_id}
            to={`/worlds/${world.entity_id}`}
            className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200 overflow-hidden"
          >
            {/* World Header */}
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Globe className="text-blue-600" size={24} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg text-gray-900">{world.name}</h3>
                    <p className="text-sm text-gray-500">{world.entity_id}</p>
                  </div>
                </div>
              </div>
              
              <p className="text-gray-600 mt-3 text-sm line-clamp-2">
                {world.description}
              </p>
              
              <div className="mt-3 px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-700 inline-block">
                {world.general_mood}
              </div>
            </div>

            {/* World Stats */}
            <div className="p-4 bg-gray-50">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <MapPin size={16} className="text-gray-500" />
                  <span className="text-gray-600">
                    {world.pill?.region_count || 0} Regionen
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Users size={16} className="text-gray-500" />
                  <span className="text-gray-600">
                    {world.pill?.total_locations || 0} Orte
                  </span>
                </div>
              </div>
              
              {world.pill?.magic_system_type && (
                <div className="mt-2 text-xs text-blue-600 font-medium">
                  🔮 {world.pill.magic_system_type}
                </div>
              )}
              
              {world.pill?.key_religions && world.pill.key_religions.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {world.pill.key_religions.slice(0, 2).map((religion, index) => (
                    <span key={index} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded">
                      {religion}
                    </span>
                  ))}
                  {world.pill.key_religions.length > 2 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                      +{world.pill.key_religions.length - 2}
                    </span>
                  )}
                </div>
              )}
            </div>
          </Link>
        ))}
      </div>

      {/* Empty State */}
      {worlds.length === 0 && (
        <div className="text-center py-12">
          <Globe size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Keine Welten vorhanden</h3>
          <p className="text-gray-600 mb-4">Erstelle deine erste Fantasy-Welt um zu beginnen.</p>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 mx-auto transition-colors">
            <Plus size={20} />
            Erste Welt erstellen
          </button>
        </div>
      )}
    </div>
  );
};

export default WorldList; 