import { useState, useEffect, useRef } from "react";

const useMouseTracking = (username, currentPage) => {
  const resolveBackendUrl = () => {
    try {
      const envUrl = import.meta?.env?.VITE_API_URL;
      if (envUrl) return envUrl.replace(/\/+$/, "");
    } catch {
      // import.meta may not exist in some environments during static analysis — ignore
    }

    return "http://localhost:5000";
  };

  const BACKEND_URL = resolveBackendUrl();

  const [events, setEvents] = useState([]);
  const mousePos = useRef({ x: 0, y: 0 });
  const eventsRef = useRef([]); // Ref to keep track of events without dependency issues
  const lastMoveEventTime = useRef(0); // Track last mousemove event timestamp for throttling

  // Update ref whenever state changes
  useEffect(() => {
    eventsRef.current = events;
  }, [events]);

  const [isVisible, setIsVisible] = useState(
    document.visibilityState === "visible"
  );

  // Track visibility
  useEffect(() => {
    const handleVisibilityChange = () => {
      const visible = document.visibilityState === "visible";
      setIsVisible(visible);
      console.log("Visibility changed:", visible ? "Visible" : "Hidden");
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () =>
      document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, []);

  // Track mouse position with throttled mousemove events
  useEffect(() => {
    const THROTTLE_MS = 500; // Sample mousemove events every 500ms

    const handleMouseMove = (e) => {
      if (!isVisible) return;

      const now = Date.now();
      mousePos.current = { x: e.clientX, y: e.clientY };

      // Throttle: only send mousemove event if enough time has passed
      if (now - lastMoveEventTime.current >= THROTTLE_MS) {
        lastMoveEventTime.current = now;

        const newEvent = {
          username: username || "unknown",
          action: "mouse move",
          page: currentPage,
          timestamp: now,
          x: e.clientX,
          y: e.clientY,
        };
        setEvents((prev) => [...prev, newEvent]);
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [username, currentPage, isVisible]);

  // Track clicks
  useEffect(() => {
    const handleClick = (e) => {
      if (!isVisible) return;
      const newEvent = {
        username: username || "unknown",
        action: "mouse click",
        page: currentPage,
        timestamp: Date.now(),
        x: e.clientX,
        y: e.clientY,
      };
      setEvents((prev) => [...prev, newEvent]);
    };

    window.addEventListener("mousedown", handleClick);
    return () => window.removeEventListener("mousedown", handleClick);
  }, [username, currentPage, isVisible]);

  // Interval: 5s sampling (Mouse Idle/Position check)
  useEffect(() => {
    const interval = setInterval(() => {
      if (!isVisible) return;
      const newEvent = {
        username: username || "unknown",
        action: "mouse idle",
        page: currentPage,
        timestamp: Date.now(),
        x: mousePos.current.x,
        y: mousePos.current.y,
      };
      setEvents((prev) => [...prev, newEvent]);
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
        const response = await fetch(`${BACKEND_URL}/collect`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error("Failed to send");
      } catch (error) {
        console.error("Failed to send mouse events:", error);
        // Optional: Put events back if failed? For now, we drop them to avoid memory leaks.
        setEvents(payload);
      }
    }, 30000);

    return () => clearInterval(flushInterval);
  }, [isVisible, BACKEND_URL]);

  return {};
};

export default useMouseTracking;
