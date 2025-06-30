import React from 'react';
import { Link } from 'react-router-dom';

function Navigation() {
  return (
    <nav className="nav">
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/characters">Characters</Link></li>
        <li><Link to="/campaigns">Campaigns</Link></li>
        <li><Link to="/worlds">Welten</Link></li>
      </ul>
    </nav>
  );
}

export default Navigation; 