import { useState, useEffect, useRef } from 'react';

const useMouseTracking = (username, currentPage) => {
    // Resolve backend URL dynamically:
    // 1) Use Vite env var `VITE_API_URL` when provided (recommended)
    // 2) Fallback to `window.location.origin` so the frontend will call the same origin
    // 3) Final fallback to localhost:5000 for local dev
    const resolveBackendUrl = () => {
        try {
            // Access via window.__VITE_ENV__ or directly from import.meta.env
            const envUrl = import.meta.env.VITE_API_URL;
            if (envUrl) return envUrl.replace(/\/+$/, '');
        } catch (e) {
            console.warn('[useMouseTracking] Error accessing import.meta.env:', e);
            // import.meta may not exist in some environments during static analysis — ignore
        }

        if (typeof window !== 'undefined' && window.location) {
            const fallback = window.location.origin.replace(/\/+$/, '');
            return fallback;
        }

        return 'http://localhost:5000';
    };

    const BACKEND_URL = resolveBackendUrl();

    const [events, setEvents] = useState([]);
    const mousePos = useRef({ x: 0, y: 0 });
    const eventsRef = useRef([]); // Ref to keep track of events without dependency issues

    // Update ref whenever state changes
    useEffect(() => {
        eventsRef.current = events;
    }, [events]);

    const [isVisible, setIsVisible] = useState(document.visibilityState === 'visible');

    // Track visibility
    useEffect(() => {
        const handleVisibilityChange = () => {
            const visible = document.visibilityState === 'visible';
            setIsVisible(visible);
            console.log('Visibility changed:', visible ? 'Visible' : 'Hidden');
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
    }, []);

    // Track mouse position
    useEffect(() => {
        const handleMouseMove = (e) => {
            if (!isVisible) return;
            mousePos.current = { x: e.clientX, y: e.clientY };
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, [isVisible]);

    // Track clicks
    useEffect(() => {
        const handleClick = (e) => {
            if (!isVisible) return;
            const newEvent = {
                username: username || 'unknown',
                action: 'mouse click',
                page: currentPage,
                timestamp: Date.now(),
                x: e.clientX,
                y: e.clientY
            };
            setEvents(prev => [...prev, newEvent]);
        };

        window.addEventListener('mousedown', handleClick);
        return () => window.removeEventListener('mousedown', handleClick);
    }, [username, currentPage, isVisible]);

    // Interval: 5s sampling (Mouse Idle/Position check)
    useEffect(() => {
        const interval = setInterval(() => {
            if (!isVisible) return;
            const newEvent = {
                username: username || 'unknown',
                action: 'mouse idle',
                page: currentPage,
                timestamp: Date.now(),
                x: mousePos.current.x,
                y: mousePos.current.y
            };
            setEvents(prev => [...prev, newEvent]);
        }, 5000);

        return () => clearInterval(interval);
    }, [username, currentPage, isVisible]);

    // Interval: 30s flush to backend
    useEffect(() => {
        const flushInterval = setInterval(async () => {
            if (!isVisible) return;
            if (eventsRef.current.length === 0) return;

            const payload = [...eventsRef.current];
            // Clear buffer immediately to avoid duplicates if request takes time
            setEvents([]);

            try {
                // Use /api/collect which proxies to backend in dev, or construct full URL in prod
                const url = `${BACKEND_URL}/collect`
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });
                console.log('[useMouseTracking] Fetch response status:', response);
            } catch (error) {
                console.error('[useMouseTracking] Failed to send mouse events:', error);
                // Optional: Put events back if failed? For now, we drop them to avoid memory leaks.
            }
        }, 5000);

        return () => clearInterval(flushInterval);
    }, [isVisible, BACKEND_URL]);

    return {};
};

export default useMouseTracking;
