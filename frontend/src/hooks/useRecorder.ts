import { useState, useRef, useCallback } from 'react';

const MIME_TYPE_CANDIDATES = [
  'audio/webm;codecs=opus',
  'audio/webm',
  'audio/mp4',
  'audio/ogg;codecs=opus',
];

function getSupportedMimeType() {
  if (typeof MediaRecorder === 'undefined') return '';
  return MIME_TYPE_CANDIDATES.find(type => MediaRecorder.isTypeSupported(type)) ?? '';
}

export function useRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const stopResolverRef = useRef<((blob: Blob | null) => void) | null>(null);

  const cleanupStream = useCallback(() => {
    streamRef.current?.getTracks().forEach(track => track.stop());
    streamRef.current = null;
  }, []);

  const start = useCallback(async () => {
    setError(null);
    setAudioBlob(null);
    setIsPaused(false);
    chunksRef.current = [];

    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      setError('Ваш браузер не поддерживает запись аудио. Попробуйте Chrome, Edge или Safari последней версии.');
      return false;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = getSupportedMimeType();
      const mediaRecorder = new MediaRecorder(
        stream,
        mimeType ? { mimeType } : undefined,
      );

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };

      mediaRecorder.onerror = () => {
        setError('Во время записи произошла ошибка. Попробуйте ещё раз.');
      };

      mediaRecorder.onstop = () => {
        const blobType = mediaRecorder.mimeType || mimeType || 'audio/webm';
        const blob = new Blob(chunksRef.current, { type: blobType });
        setAudioBlob(blob);
        setIsRecording(false);
        setIsPaused(false);
        cleanupStream();
        mediaRecorderRef.current = null;
        stopResolverRef.current?.(blob);
        stopResolverRef.current = null;
      };

      mediaRecorder.start(250);
      setIsRecording(true);
      setIsPaused(false);
      return true;
    } catch (caughtError) {
      console.error(caughtError);
      cleanupStream();
      mediaRecorderRef.current = null;
      setIsRecording(false);
      setIsPaused(false);
      setError('Не удалось получить доступ к микрофону. Проверьте разрешения браузера.');
      return false;
    }
  }, [cleanupStream]);

  const pause = useCallback(() => {
    const recorder = mediaRecorderRef.current;

    if (!recorder || recorder.state !== 'recording') return false;

    recorder.pause();
    setIsRecording(false);
    setIsPaused(true);
    return true;
  }, []);

  const resume = useCallback(() => {
    const recorder = mediaRecorderRef.current;

    if (!recorder) return false;

    if (recorder.state === 'paused') {
      recorder.resume();
      setIsRecording(true);
      setIsPaused(false);
      return true;
    }

    if (recorder.state === 'recording') {
      setIsRecording(true);
      setIsPaused(false);
      return true;
    }

    return false;
  }, []);

  const stop = useCallback(() => {
    return new Promise<Blob | null>((resolve) => {
      const recorder = mediaRecorderRef.current;

      if (!recorder || recorder.state === 'inactive') {
        setIsRecording(false);
        setIsPaused(false);
        cleanupStream();
        resolve(null);
        return;
      }

      stopResolverRef.current = resolve;
      recorder.stop();
    });
  }, [cleanupStream]);

  return { isRecording, isPaused, audioBlob, error, start, pause, resume, stop };
}
