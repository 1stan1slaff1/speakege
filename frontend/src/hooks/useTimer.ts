import { useState, useEffect, useRef, useCallback } from 'react';

export function useTimer(initialSeconds: number, onComplete: () => void) {
  const [secondsLeft, setSecondsLeft] = useState(initialSeconds);
  const [isRunning, setIsRunning] = useState(false);
  const expectedRef = useRef<number | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onCompleteRef = useRef(onComplete);

  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  const tick = useCallback(() => {
    const now = Date.now();
    const drift = now - (expectedRef.current ?? now);

    setSecondsLeft(prev => {
      if (prev <= 1) {
        setIsRunning(false);
        onCompleteRef.current();
        return 0;
      }
      return prev - 1;
    });

    expectedRef.current = now + 1000 - drift;
    timeoutRef.current = setTimeout(tick, Math.max(0, 1000 - drift));
  }, []);

  const start = useCallback(() => {
    setSecondsLeft(initialSeconds);
    setIsRunning(true);
    expectedRef.current = Date.now() + 1000;
    timeoutRef.current = setTimeout(tick, 1000);
  }, [initialSeconds, tick]);

  const stop = useCallback(() => {
    setIsRunning(false);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
  }, []);

  const reset = useCallback(() => {
    stop();
    setSecondsLeft(initialSeconds);
  }, [stop, initialSeconds]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;
  const display = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  return { secondsLeft, isRunning, display, start, stop, reset };
}
