import React from 'react';

const Confirmation = ({ pokemon, onReset }) => {
    return (
        <div style={{
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            textAlign: 'center',
            padding: '2rem'
        }}>
            <div className="anime-card" style={{ maxWidth: '600px', width: '100%', padding: '3rem' }}>
                <h2 className="title-text" style={{ fontSize: '2.5rem' }}>Adventure Awaits!</h2>

                <div style={{ margin: '2rem 0' }}>
                    <img
                        src={pokemon.img}
                        alt={pokemon.name}
                        className="fade-in"
                        style={{
                            width: '200px',
                            height: '200px',
                            objectFit: 'contain',
                            filter: `drop-shadow(0 0 20px ${pokemon.color})`
                        }}
                    />
                    <h3 style={{ fontSize: '2rem', margin: '1rem 0', color: pokemon.color }}>{pokemon.name}</h3>
                    <p style={{ fontSize: '1.2rem', opacity: 0.8 }}>
                        You have successfully chosen {pokemon.name} as your partner.
                        <br />
                        Your journey begins now!
                    </p>
                </div>

                <button className="anime-btn" onClick={onReset}>
                    Start Over
                </button>
            </div>
        </div>
    );
};

export default Confirmation;
