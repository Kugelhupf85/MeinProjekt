import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header.jsx';
import Navigation from './components/Navigation.jsx';
import Home from './components/Home.jsx';
import Characters from './components/Characters.jsx';
import Campaigns from './components/Campaigns.jsx';
import WorldList from './components/WorldList.jsx';
import WorldDetail from './components/WorldDetail.jsx';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Navigation />
        <div className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/characters" element={<Characters />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/worlds" element={<WorldList />} />
            <Route path="/worlds/:worldId" element={<WorldDetail />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App; 