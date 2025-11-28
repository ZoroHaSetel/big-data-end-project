import React, { useState } from 'react';

const Login = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleLogin = (e) => {
        e.preventDefault();
        // Hardcoded credentials as per requirements
        const users = [
            { u: 'ash', p: 'pikachu123' },
            { u: 'misty', p: 'togepi456' },
            { u: 'brock', p: 'onix789' }
        ];

        const isValid = users.some(user => user.u === username && user.p === password);

        if (isValid) {
            onLogin(username);
        } else {
            setError('Invalid Trainer ID or Password');
        }
    };

    return (
        <div className="login-container" style={{
            height: '100vh',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
        }}>
            <div className="anime-card" style={{ width: '100%', maxWidth: '400px' }}>
                <h2 className="title-text" style={{ fontSize: '2.5rem', textAlign: 'center' }}>Trainer Login</h2>

                <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--secondary)' }}>Trainer ID</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '12px',
                                background: 'rgba(255,255,255,0.05)',
                                border: '1px solid var(--glass-border)',
                                borderRadius: '8px',
                                color: 'white',
                                outline: 'none'
                            }}
                        />
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--secondary)' }}>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '12px',
                                background: 'rgba(255,255,255,0.05)',
                                border: '1px solid var(--glass-border)',
                                borderRadius: '8px',
                                color: 'white',
                                outline: 'none'
                            }}
                        />
                    </div>

                    {error && <p style={{ color: 'var(--primary)', textAlign: 'center' }}>{error}</p>}

                    <button type="submit" className="anime-btn" style={{ width: '100%', marginTop: '1rem' }}>
                        Enter System
                    </button>
                </form>

                <div style={{ marginTop: '2rem', fontSize: '0.8rem', opacity: 0.6, textAlign: 'center' }}>
                    <p>Default Access:</p>
                    <p>ash / pikachu123</p>
                    <p>misty / togepi456</p>
                    <p>brock / onix789</p>
                </div>
            </div>
        </div>
    );
};

export default Login;
