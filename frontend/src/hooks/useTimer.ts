import { useState, useEffect, useRef, useCallback } from 'react';

function formatSeconds(totalSeconds: number) {
  const safeSeconds = Math.max(0, Math.ceil(totalSeconds));
  const minutes = Math.floor(safeSeconds / 60);
  const seconds = safeSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

export function useTimer(initialSeconds: number, onComplete: () => void) {
  const [secondsLeft, setSecondsLeft] = useState(initialSeconds);
  const [isRunning, setIsRunning] = useState(false);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const endAtRef = useRef<number | null>(null);
  const onCompleteRef = useRef(onComplete);
  const completedRef = useRef(false);

  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  const clearIntervalRef = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const finish = useCallback(() => {
    clearIntervalRef();
    endAtRef.current = null;
    setSecondsLeft(0);
    setIsRunning(false);

    if (!completedRef.current) {
      completedRef.current = true;
      onCompleteRef.current();
    }
  }, [clearIntervalRef]);

  const updateFromClock = useCallback(() => {
    if (!endAtRef.current) return;

    const millisecondsLeft = endAtRef.current - Date.now();

    if (millisecondsLeft <= 0) {
      finish();
      return;
    }

    setSecondsLeft(Math.ceil(millisecondsLeft / 1000));
  }, [finish]);

  const start = useCallback((durationSeconds = initialSeconds) => {
    clearIntervalRef();
    completedRef.current = false;

    const normalizedDuration = Math.max(0, durationSeconds);
    setSecondsLeft(normalizedDuration);

    if (normalizedDuration === 0) {
      finish();
      return;
    }

    endAtRef.current = Date.now() + normalizedDuration * 1000;
    setIsRunning(true);
    intervalRef.current = setInterval(updateFromClock, 250);
  }, [clearIntervalRef, finish, initialSeconds, updateFromClock]);

  const stop = useCallback(() => {
    clearIntervalRef();
    endAtRef.current = null;
    setIsRunning(false);
  }, [clearIntervalRef]);

  const reset = useCallback((durationSeconds = initialSeconds) => {
    stop();
    completedRef.current = false;
    setSecondsLeft(Math.max(0, durationSeconds));
  }, [initialSeconds, stop]);

  useEffect(() => {
    return clearIntervalRef;
  }, [clearIntervalRef]);

  return {
    secondsLeft,
    isRunning,
    display: formatSeconds(secondsLeft),
    start,
    stop,
    reset,
  };
}
