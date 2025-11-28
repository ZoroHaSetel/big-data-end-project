import React from 'react';

const LandingPage = ({ onStart }) => {
  return (
    <div className="landing-container" style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      textAlign: 'center',
      padding: '2rem'
    }}>
      <div className="fade-in">
        <h1 className="title-text">Pokemon<br/>Legends</h1>
        <p style={{ fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto 2rem', opacity: 0.8 }}>
          Begin your journey in a world of dreams and adventures. 
          Choose your partner and become the very best.
        </p>
        
        <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center', marginBottom: '3rem' }}>
          {/* Placeholder for starter silhouettes or icons */}
          <div className="anime-card" style={{ width: '100px', height: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🔥</div>
          <div className="anime-card" style={{ width: '100px', height: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>💧</div>
          <div className="anime-card" style={{ width: '100px', height: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🍃</div>
        </div>

        <button className="anime-btn" onClick={onStart}>
          Start Adventure
        </button>
      </div>
    </div>
  );
};

export default LandingPage;
