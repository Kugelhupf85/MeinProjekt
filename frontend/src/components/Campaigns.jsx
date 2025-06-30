import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const response = await axios.get('/api/campaigns/');
        setCampaigns(response.data.results || response.data);
        setLoading(false);
      } catch (err) {
        setError('Fehler beim Laden der Kampagnen: ' + err.message);
        setLoading(false);
      }
    };

    fetchCampaigns();
  }, []);

  if (loading) return <div>Laden...</div>;
  if (error) return <div>Fehler: {error}</div>;

  return (
    <div>
      <h2>Kampagnen</h2>
      {campaigns.length === 0 ? (
        <p>Keine Kampagnen gefunden. Erstellen Sie welche über das Django Admin Interface!</p>
      ) : (
        <div>
          {campaigns.map((campaign) => (
            <div key={campaign.id} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
              <h3>{campaign.name}</h3>
              <p>{campaign.description}</p>
              <p>Dungeon Master: {campaign.dungeon_master?.username || 'Unbekannt'}</p>
              <p>Spieler: {campaign.players?.length || 0}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Campaigns; 