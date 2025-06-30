import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Globe, MapPin, Users, Calendar, Languages, Sparkles, Sword, Mountain, Coins } from 'lucide-react';

const WorldDetail = () => {
  const { worldId } = useParams();
  const [world, setWorld] = useState(null);
  const [regions, setRegions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWorldDetail();
  }, [worldId]);

  const fetchWorldDetail = async () => {
    try {
      setLoading(true);
      
      // Mock data for world detail
      const mockWorld = {
        entity_id: worldId,
        name: worldId === 'WLD-123456789012' ? 'Mittelerde' : 'Drachenlande',
        description: worldId === 'WLD-123456789012' 
          ? 'Eine epische Fantasy-Welt voller Magie und Abenteuer. Mittelerde ist ein Reich der Elben, Zwerge, Menschen und Hobbits, wo uralte Mächte und dunkle Schatten um die Vorherrschaft kämpfen.'
          : 'Ein Reich der Drachen und mutigen Helden. Die Drachenlande sind geprägt von majestätischen Drachen, die über schroffe Berge und tiefe Täler herrschen.',
        general_mood: worldId === 'WLD-123456789012' ? 'Episch und mystisch' : 'Gefährlich und aufregend',
        current_date: '3. Zeitalter, Jahr 3019',
        pill: {
          region_count: worldId === 'WLD-123456789012' ? 5 : 3,
          total_locations: worldId === 'WLD-123456789012' ? 23 : 15,
          key_religions: worldId === 'WLD-123456789012' 
            ? ['Valar-Verehrung', 'Naturgeister', 'Ahnenverehrung']
            : ['Drachenkult', 'Kriegsgötter', 'Elementargeister'],
          primary_languages: worldId === 'WLD-123456789012'
            ? ['Sindarin', 'Westron', 'Khuzdul']
            : ['Drakonisch', 'Gemeinsprache', 'Alte Runen'],
          magic_system_type: worldId === 'WLD-123456789012' ? 'Göttliche Magie' : 'Elementarmagie',
          major_conflicts: worldId === 'WLD-123456789012'
            ? ['Der Ring-Krieg', 'Schatten im Osten']
            : ['Drachenkriege', 'Territoriale Kämpfe'],
          climate_summary: worldId === 'WLD-123456789012'
            ? ['Gemäßigt', 'Mediterran', 'Gebirgsklima']
            : ['Kontinental', 'Gebirgsklima', 'Vulkanisch']
        },
        created_at: '2025-06-08T00:00:00Z'
      };

      const mockRegions = worldId === 'WLD-123456789012' ? [
        {
          entity_id: 'RGN-111111111111',
          name: 'Auenland',
          description: 'Die friedliche Heimat der Hobbits',
          terrain_type: 'Hügelland',
          pill: {
            location_count: 8,
            government_type: 'Dorfgemeinschaft',
            primary_currency: { name: 'Hobbit-Münzen', symbol: 'HM' },
            major_personalities: ['Bilbo Beutlin', 'Frodo Beutlin'],
            key_settlements: ['Hobbingen', 'Bockland', 'Tuckborough']
          }
        },
        {
          entity_id: 'RGN-222222222222',
          name: 'Gondor',
          description: 'Das mächtige Königreich der Menschen',
          terrain_type: 'Ebenen und Berge',
          pill: {
            location_count: 12,
            government_type: 'Königreich',
            primary_currency: { name: 'Gondor-Gold', symbol: 'GG' },
            major_personalities: ['Aragorn', 'Boromir', 'Denethor'],
            key_settlements: ['Minas Tirith', 'Osgiliath', 'Dol Amroth']
          }
        }
      ] : [
        {
          entity_id: 'RGN-333333333333',
          name: 'Drachenberge',
          description: 'Die schroffen Berge der alten Drachen',
          terrain_type: 'Hochgebirge',
          pill: {
            location_count: 7,
            government_type: 'Drachenrat',
            primary_currency: { name: 'Drachenschuppen', symbol: 'DS' },
            major_personalities: ['Smaug der Goldene', 'Ancalagon'],
            key_settlements: ['Erebor', 'Drachenhort', 'Feuerspitze']
          }
        }
      ];

      setWorld(mockWorld);
      setRegions(mockRegions);
      setError(null);
    } catch (err) {
      setError('Fehler beim Laden der Welt: ' + err.message);
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

  if (!world) {
    return (
      <div className="text-center py-12">
        <Globe size={48} className="mx-auto text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Welt nicht gefunden</h3>
        <Link to="/worlds" className="text-blue-600 hover:text-blue-700">
          Zurück zur Weltenliste
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link 
          to="/worlds" 
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft size={20} className="text-gray-600" />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">{world.name}</h1>
          <p className="text-gray-600 mt-1">{world.entity_id}</p>
        </div>
      </div>

      {/* World Overview */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Globe className="text-blue-600" size={32} />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Weltbeschreibung</h2>
              <p className="text-gray-700 leading-relaxed">{world.description}</p>
              
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full">
                  {world.general_mood}
                </span>
                <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full flex items-center gap-1">
                  <Calendar size={14} />
                  {world.current_date}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* World Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <MapPin className="text-blue-600" size={24} />
            <div>
              <p className="text-2xl font-bold text-gray-900">{world.pill.region_count}</p>
              <p className="text-sm text-gray-600">Regionen</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <Users className="text-green-600" size={24} />
            <div>
              <p className="text-2xl font-bold text-gray-900">{world.pill.total_locations}</p>
              <p className="text-sm text-gray-600">Orte</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <Languages className="text-purple-600" size={24} />
            <div>
              <p className="text-2xl font-bold text-gray-900">{world.pill.primary_languages?.length || 0}</p>
              <p className="text-sm text-gray-600">Sprachen</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <Sparkles className="text-yellow-600" size={24} />
            <div>
              <p className="text-sm font-medium text-gray-900">{world.pill.magic_system_type}</p>
              <p className="text-sm text-gray-600">Magie-System</p>
            </div>
          </div>
        </div>
      </div>

      {/* World Details Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Languages */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Languages className="text-purple-600" size={20} />
            Sprachen
          </h3>
          <div className="space-y-2">
            {world.pill.primary_languages?.map((language, index) => (
              <div key={index} className="px-3 py-2 bg-purple-50 rounded-lg text-purple-700">
                {language}
              </div>
            ))}
          </div>
        </div>

        {/* Religions */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Sparkles className="text-yellow-600" size={20} />
            Religionen
          </h3>
          <div className="space-y-2">
            {world.pill.key_religions?.map((religion, index) => (
              <div key={index} className="px-3 py-2 bg-yellow-50 rounded-lg text-yellow-700">
                {religion}
              </div>
            ))}
          </div>
        </div>

        {/* Conflicts */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Sword className="text-red-600" size={20} />
            Konflikte
          </h3>
          <div className="space-y-2">
            {world.pill.major_conflicts?.map((conflict, index) => (
              <div key={index} className="px-3 py-2 bg-red-50 rounded-lg text-red-700">
                {conflict}
              </div>
            ))}
          </div>
        </div>

        {/* Climate */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Mountain className="text-green-600" size={20} />
            Klimazonen
          </h3>
          <div className="space-y-2">
            {world.pill.climate_summary?.map((climate, index) => (
              <div key={index} className="px-3 py-2 bg-green-50 rounded-lg text-green-700">
                {climate}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Regions */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">Regionen</h3>
          <p className="text-gray-600 mt-1">Erkunde die verschiedenen Regionen dieser Welt</p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {regions.map((region) => (
              <div key={region.entity_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">{region.name}</h4>
                    <p className="text-sm text-gray-500">{region.entity_id}</p>
                  </div>
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                    {region.terrain_type}
                  </span>
                </div>
                
                <p className="text-gray-600 text-sm mb-3">{region.description}</p>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-1">
                    <MapPin size={12} className="text-gray-500" />
                    <span>{region.pill.location_count} Orte</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Coins size={12} className="text-gray-500" />
                    <span>{region.pill.primary_currency?.symbol}</span>
                  </div>
                </div>
                
                {region.pill.key_settlements && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {region.pill.key_settlements.slice(0, 2).map((settlement, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        {settlement}
                      </span>
                    ))}
                    {region.pill.key_settlements.length > 2 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        +{region.pill.key_settlements.length - 2}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorldDetail; 