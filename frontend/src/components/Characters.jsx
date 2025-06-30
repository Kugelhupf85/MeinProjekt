import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Characters() {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const response = await axios.get('/api/characters/');
        setCharacters(response.data.results || response.data);
        setLoading(false);
      } catch (err) {
        setError('Fehler beim Laden der Charaktere: ' + err.message);
        setLoading(false);
      }
    };

    fetchCharacters();
  }, []);

  if (loading) return <div>Laden...</div>;
  if (error) return <div>Fehler: {error}</div>;

  return (
    <div>
      <h2>Charaktere</h2>
      {characters.length === 0 ? (
        <p>Keine Charaktere gefunden. Erstellen Sie welche über das Django Admin Interface!</p>
      ) : (
        <div>
          {characters.map((character) => (
            <div key={character.id} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
              <h3>{character.name}</h3>
              <p>Klasse: {character.character_class}</p>
              <p>Level: {character.level}</p>
              <p>Besitzer: {character.owner?.username || 'Unbekannt'}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Characters; 