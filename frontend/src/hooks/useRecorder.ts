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
        cleanupStream();
        mediaRecorderRef.current = null;
        stopResolverRef.current?.(blob);
        stopResolverRef.current = null;
      };

      mediaRecorder.start(250);
      setIsRecording(true);
      return true;
    } catch (caughtError) {
      console.error(caughtError);
      cleanupStream();
      mediaRecorderRef.current = null;
      setIsRecording(false);
      setError('Не удалось получить доступ к микрофону. Проверьте разрешения браузера.');
      return false;
    }
  }, [cleanupStream]);

  const stop = useCallback(() => {
    return new Promise<Blob | null>((resolve) => {
      const recorder = mediaRecorderRef.current;

      if (!recorder || recorder.state === 'inactive') {
        setIsRecording(false);
        cleanupStream();
        resolve(null);
        return;
      }

      stopResolverRef.current = resolve;
      recorder.stop();
    });
  }, [cleanupStream]);

  return { isRecording, audioBlob, error, start, stop };
}
