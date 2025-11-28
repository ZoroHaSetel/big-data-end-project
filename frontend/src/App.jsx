import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import Login from './components/Login';
import PokemonSelection from './components/PokemonSelection';
import Confirmation from './components/Confirmation';
import useMouseTracking from './hooks/useMouseTracking';

function App() {
  const [view, setView] = useState('landing'); // landing, login, selection, confirmation
  const [user, setUser] = useState(null);
  const [selectedPokemon, setSelectedPokemon] = useState(null);

  useMouseTracking(user, view);

  const handleStart = () => {
    setView('login');
  };

  const handleLogin = (username) => {
    setUser(username);
    setView('selection');
  };

  const handleSelect = (pokemon) => {
    setSelectedPokemon(pokemon);
    setView('confirmation');
  };

  const handleReset = () => {
    setView('landing');
    setUser(null);
    setSelectedPokemon(null);
  };

  return (
    <>
      {view === 'landing' && <LandingPage onStart={handleStart} />}
      {view === 'login' && <Login onLogin={handleLogin} />}
      {view === 'selection' && <PokemonSelection onSelect={handleSelect} />}
      {view === 'confirmation' && <Confirmation pokemon={selectedPokemon} onReset={handleReset} />}
    </>
  );
}

export default App;
