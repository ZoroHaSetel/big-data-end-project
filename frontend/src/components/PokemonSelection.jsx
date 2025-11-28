import React, { useState } from 'react';

const PokemonSelection = ({ onSelect }) => {
    const [selectedId, setSelectedId] = useState(null);

    const starters = [
        { id: 1, name: 'Bulbasaur', type: 'Grass', color: '#78C850', img: 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png' },
        { id: 4, name: 'Charmander', type: 'Fire', color: '#F08030', img: 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png' },
        { id: 7, name: 'Squirtle', type: 'Water', color: '#6890F0', img: 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png' }
    ];

    const handleConfirm = () => {
        if (selectedId) {
            const pokemon = starters.find(p => p.id === selectedId);
            onSelect(pokemon);
        }
    };

    return (
        <div style={{ minHeight: '100vh', padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h2 className="title-text" style={{ fontSize: '3rem', textAlign: 'center' }}>Choose Your Partner</h2>

            <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '2rem',
                justifyContent: 'center',
                marginTop: '3rem',
                marginBottom: '3rem'
            }}>
                {starters.map(pokemon => (
                    <div
                        key={pokemon.id}
                        className="anime-card"
                        onClick={() => setSelectedId(pokemon.id)}
                        style={{
                            width: '250px',
                            cursor: 'pointer',
                            border: selectedId === pokemon.id ? `2px solid ${pokemon.color}` : '1px solid var(--glass-border)',
                            transform: selectedId === pokemon.id ? 'scale(1.05)' : 'scale(1)',
                            background: selectedId === pokemon.id ? `linear-gradient(180deg, rgba(255,255,255,0.1), ${pokemon.color}22)` : 'var(--glass)'
                        }}
                    >
                        <img
                            src={pokemon.img}
                            alt={pokemon.name}
                            style={{ width: '100%', height: '250px', objectFit: 'contain', filter: 'drop-shadow(0 0 10px rgba(0,0,0,0.5))' }}
                        />
                        <h3 style={{ textAlign: 'center', fontSize: '1.5rem', margin: '1rem 0 0.5rem' }}>{pokemon.name}</h3>
                        <div style={{
                            textAlign: 'center',
                            background: pokemon.color,
                            color: 'white',
                            padding: '4px 12px',
                            borderRadius: '20px',
                            display: 'inline-block',
                            width: '100%',
                            fontWeight: 'bold'
                        }}>
                            {pokemon.type}
                        </div>
                    </div>
                ))}
            </div>

            <button
                className="anime-btn"
                onClick={handleConfirm}
                disabled={!selectedId}
                style={{
                    opacity: selectedId ? 1 : 0.5,
                    cursor: selectedId ? 'pointer' : 'not-allowed',
                    fontSize: '1.2rem'
                }}
            >
                I Choose You!
            </button>
        </div>
    );
};

export default PokemonSelection;
