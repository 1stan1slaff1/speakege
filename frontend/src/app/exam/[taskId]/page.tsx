'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { TASK_CONFIG, TaskType, RecordingSegment } from '@/config/tasks';
import { useTimer } from '@/hooks/useTimer';
import { useRecorder } from '@/hooks/useRecorder';
import Timer from '@/components/exam/Timer';
import TaskDisplay from '@/components/exam/TaskDisplay';

type Phase = 'idle' | 'checking' | 'preparing' | 'starting' | 'recording' | 'submitting';

const MAX_AUDIO_BYTES = 16 * 1024 * 1024;
const ACCEPTED_AUDIO_TYPES = 'audio/webm,audio/ogg,audio/mpeg,audio/mp3,audio/mp4,audio/m4a,audio/x-m4a,audio/aac,audio/wav,audio/x-wav,.webm,.ogg,.mp3,.mp4,.m4a,.aac,.wav';
const ACCEPTED_AUDIO_EXTENSIONS = ['webm', 'ogg', 'mp3', 'mp4', 'm4a', 'aac', 'wav'];

interface DemoQuestion {
  promptText: string;
  imageUrl?: string;
}

const DEMO_QUESTIONS: Record<TaskType, DemoQuestion> = {
  task1: {
    promptText: `Imagine that you are preparing a project with your friend. You have found some interesting material for the presentation and you want to read this text to your friend. You have 1.5 minutes to read the text silently, then be ready to read it out aloud. You will not have more than 1.5 minutes to read it.

Snowflakes are ice crystals which fall through the Earth's atmosphere as snow. People like to think that every snowflake has a unique shape. However, it is not true. While snowflakes may look different, they can still be classified into eight groups and about eighty different variants. Some scientists have done a lot of research into making a kind of catalogue of snowflakes.

The most typical patterns for a snowflake are needles, columns, plates and rimes. The shape and the pattern of a snowflake largely depend on the weather conditions. The study of snowflakes has identified that long, thin needle-like ice crystals form at around zero, while a lower temperature will lead to very flat crystals. Further changes in temperature as a snowflake falls determine more complicated shapes of snowflakes. The size of a snowflake also depends on the air temperature.`,
  },
  task2: {
    promptText: `Study the advertisement.

THE BEST CLINIC IN TOWN!

You are considering visiting the clinic and now you would like to get more information. In 1.5 minutes you are to ask four direct questions to find out about the following:

1) location
2) public transport
3) dentist
4) family discounts

You have 20 seconds to ask each question.`,
  },
  task3: {
    promptText: `You are going to give an interview. You have to answer five questions. Give full answers to the questions: 2–3 sentences.

Remember that you have 40 seconds to answer each question.

Interviewer: Hello! It's Teenagers Round the World Channel. Our guest today is a teenager from Russia and we are going to discuss teenagers' attitude to their accommodation. Please answer five questions. So, let's get started.

1) In what region do you live? Do you live in a big city, a town or in a village?
2) Do you live in a flat or in a house? What is it like?
3) What would you like to change about your flat or house? Why?
4) What do you like and dislike about your neighbourhood?
5) What kind of housing would you like to have in the future?`,
  },
  task4: {
    promptText: `Imagine that you and your friend are doing a school project “Ideal weekend”. You have found two photos to illustrate it but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.

In 2.5 minutes be ready to:

• explain the choice of the illustrations for the project by briefly describing them and noting the differences;
• mention the advantages (1–2) of the two ways to spend the weekend;
• mention the disadvantages (1–2) of the two ways to spend the weekend;
• express your opinion on the subject of the project — say which way of spending the weekend presented in the pictures you prefer and why.

Photo 1: a family is having a picnic in a park.
Photo 2: two teenagers are watching a film at home.

You will speak for not more than 3 minutes: 12–15 sentences. You have to talk continuously.`,
  },
};

function getTaskIdFromParams(taskId: string | string[] | undefined): TaskType | null {
  if (typeof taskId !== 'string') return null;
  return taskId in TASK_CONFIG ? (taskId as TaskType) : null;
}

function formatSeconds(totalSeconds: number) {
  const safeSeconds = Math.max(0, Math.ceil(totalSeconds));
  const minutes = Math.floor(safeSeconds / 60);
  const seconds = safeSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}


function getFileExtension(fileName: string) {
  return fileName.split('.').pop()?.toLowerCase() ?? '';
}

function getAudioFilename(audio: Blob) {
  if (audio instanceof File && audio.name) return audio.name;
  if (audio.type.includes('mpeg') || audio.type.includes('mp3')) return 'recording.mp3';
  if (audio.type.includes('mp4') || audio.type.includes('m4a')) return 'recording.m4a';
  if (audio.type.includes('ogg')) return 'recording.ogg';
  if (audio.type.includes('wav')) return 'recording.wav';
  return 'recording.webm';
}

function formatFileSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
}

function validateAudioFile(file: File) {
  if (file.size === 0) return 'Файл пустой. Выберите другой аудиофайл.';
  if (file.size > MAX_AUDIO_BYTES) return 'Файл слишком большой. Максимальный размер — 16 МБ.';

  const extension = getFileExtension(file.name);
  const hasAudioMimeType = file.type.startsWith('audio/');
  const hasAcceptedExtension = ACCEPTED_AUDIO_EXTENSIONS.includes(extension);

  if (!hasAudioMimeType && !hasAcceptedExtension) {
    return 'Неподдерживаемый формат файла. Загрузите mp3, wav, m4a, mp4, webm или ogg.';
  }

  return null;
}


async function readApiError(response: Response) {
  const body = await response.text();

  if (!body) {
    return `Backend вернул ошибку ${response.status}.`;
  }

  try {
    const parsed = JSON.parse(body) as { detail?: unknown };
    if (typeof parsed.detail === 'string') return parsed.detail;
    if (parsed.detail) return JSON.stringify(parsed.detail);
  } catch {
    // The backend may return plain text or an HTML/plain 500 response.
  }

  return body;
}

function getSubmitErrorMessage(caughtError: unknown) {
  if (!(caughtError instanceof Error) || !caughtError.message) {
    return 'Не удалось отправить запись. Попробуйте ещё раз.';
  }

  if (caughtError.message === 'Failed to fetch') {
    return 'Не удалось подключиться к backend. Проверьте, что FastAPI запущен и NEXT_PUBLIC_API_URL указывает на http://localhost:8000/api.';
  }

  return caughtError.message;
}

function getCurrentSegment(segments: readonly RecordingSegment[], secondsElapsed: number) {
  let segmentStart = 0;

  for (let index = 0; index < segments.length; index += 1) {
    const segment = segments[index];
    const segmentEnd = segmentStart + segment.seconds;

    if (secondsElapsed < segmentEnd || index === segments.length - 1) {
      return {
        index,
        segment,
        secondsLeft: Math.max(0, segmentEnd - secondsElapsed),
      };
    }

    segmentStart = segmentEnd;
  }

  return null;
}

export default function ExamPage() {
  const params = useParams();
  const router = useRouter();

  const taskId = getTaskIdFromParams(params.taskId);
  const task = taskId ? TASK_CONFIG[taskId] : null;
  const question = taskId ? DEMO_QUESTIONS[taskId] : null;
  const prepSeconds = task?.prepSeconds ?? 0;
  const recordingSegments = task?.recordingSegments ?? [];
  const recordDuration = recordingSegments.reduce((sum, segment) => sum + segment.seconds, 0);

  const [phase, setPhase] = useState<Phase>('idle');
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [selectedAudioFile, setSelectedAudioFile] = useState<File | null>(null);

  const startRecordingPhaseRef = useRef<(() => Promise<void>) | null>(null);
  const finishRecordingRef = useRef<(() => Promise<void>) | null>(null);

  const {
    isRecording,
    error: recorderError,
    start: startRecording,
    stop: stopRecording,
  } = useRecorder();

  const {
    display: prepDisplay,
    isRunning: isPrepTimerRunning,
    start: startPrepTimer,
    stop: stopPrepTimer,
    reset: resetPrepTimer,
  } = useTimer(prepSeconds, () => {
    void startRecordingPhaseRef.current?.();
  });

  const {
    secondsLeft: recordSecondsLeft,
    isRunning: isRecordTimerRunning,
    start: startRecordTimer,
    stop: stopRecordTimer,
    reset: resetRecordTimer,
  } = useTimer(recordDuration, () => {
    void finishRecordingRef.current?.();
  });

  async function submitAudio(blob: Blob) {
    if (!taskId || !question) return;

    setSubmitError(null);

    try {
      const formData = new FormData();
      formData.append('audio', blob, getAudioFilename(blob));
      formData.append('task_type', taskId);
      formData.append('prompt_text', question.promptText);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
      const response = await fetch(`${apiUrl}/evaluate`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await readApiError(response);
        throw new Error(`Не удалось отправить запись: ${errorText}`);
      }

      const data = await response.json();
      router.push(`/results/${data.submission_id}?data=${encodeURIComponent(JSON.stringify(data))}`);
    } catch (caughtError) {
      console.error(caughtError);
      setSubmitError(getSubmitErrorMessage(caughtError));
      setPhase('idle');
      resetRecordTimer(recordDuration);
    }
  }

  async function finishRecording() {
    stopRecordTimer();
    setPhase('submitting');

    const blob = await stopRecording();

    if (!blob || blob.size === 0) {
      setSubmitError('Запись не получилась. Попробуйте ещё раз.');
      setPhase('idle');
      resetRecordTimer(recordDuration);
      return;
    }

    await submitAudio(blob);
  }

  async function startRecordingPhase() {
    if (!task || !question || recordDuration <= 0) return;

    setSubmitError(null);
    resetRecordTimer(recordDuration);
    setPhase('starting');

    const started = await startRecording();

    if (!started) {
      setPhase('idle');
      return;
    }

    setPhase('recording');
    startRecordTimer(recordDuration);
  }

  useEffect(() => {
    startRecordingPhaseRef.current = startRecordingPhase;
    finishRecordingRef.current = finishRecording;
  });

  async function checkMicrophone() {
    setSubmitError(null);

    if (!navigator.mediaDevices?.getUserMedia) {
      setSubmitError('Ваш браузер не поддерживает доступ к микрофону.');
      return false;
    }

    try {
      setPhase('checking');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (caughtError) {
      console.error(caughtError);
      setSubmitError('Не удалось получить доступ к микрофону. Разрешите запись аудио в браузере.');
      setPhase('idle');
      return false;
    }
  }

  async function handleStart() {
    if (!task || !question) return;

    resetPrepTimer(prepSeconds);
    resetRecordTimer(recordDuration);

    const microphoneReady = await checkMicrophone();
    if (!microphoneReady) return;

    if (prepSeconds > 0) {
      setPhase('preparing');
      startPrepTimer(prepSeconds);
    } else {
      await startRecordingPhase();
    }
  }

  async function handleSkipPrep() {
    if (phase !== 'preparing') return;

    stopPrepTimer();
    await startRecordingPhase();
  }

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setSubmitError(null);
    setSelectedAudioFile(file);

    if (file) {
      const validationError = validateAudioFile(file);
      if (validationError) setSubmitError(validationError);
    }
  }

  async function handleUploadFile() {
    if (!selectedAudioFile) {
      setSubmitError('Выберите аудиофайл для проверки.');
      return;
    }

    const validationError = validateAudioFile(selectedAudioFile);
    if (validationError) {
      setSubmitError(validationError);
      return;
    }

    setPhase('submitting');
    await submitAudio(selectedAudioFile);
  }

  if (!task || !question || !taskId) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <p className="text-red-500">Неверный тип задания.</p>
      </div>
    );
  }

  const secondsElapsed = phase === 'recording' ? recordDuration - recordSecondsLeft : 0;
  const currentSegment = getCurrentSegment(recordingSegments, secondsElapsed);
  const segmentDisplay = currentSegment ? formatSeconds(currentSegment.secondsLeft) : formatSeconds(recordSecondsLeft);
  const segmentLabel = currentSegment
    ? recordingSegments.length > 1
      ? `${currentSegment.segment.label} из ${recordingSegments.length}`
      : 'Время ответа'
    : 'Время ответа';

  return (
    <div className="max-w-3xl mx-auto p-6 min-h-screen bg-gray-50">
      <TaskDisplay
        title={task.title}
        description={task.description}
        promptText={question.promptText}
        imageUrl={question.imageUrl}
      />

      <div className="bg-white border border-gray-200 rounded-lg p-8 flex flex-col items-center gap-6">
        {phase === 'preparing' && (
          <>
            <Timer
              display={prepDisplay}
              label="Время на подготовку"
              isRunning={isPrepTimerRunning}
            />
            <button
              type="button"
              onClick={() => void handleSkipPrep()}
              className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold px-6 py-2.5 rounded-lg transition-colors"
            >
              Пропустить подготовку и начать запись
            </button>
          </>
        )}

        {phase === 'recording' && (
          <>
            <Timer
              display={segmentDisplay}
              label={segmentLabel}
              isRunning={isRecordTimerRunning}
              isRecording={isRecording}
            />

            {recordingSegments.length > 1 && currentSegment && (
              <div className="flex gap-2" aria-label="Прогресс по вопросам">
                {recordingSegments.map((segment, index) => (
                  <span
                    key={segment.label}
                    className={`h-2.5 w-10 rounded-full ${
                      index < currentSegment.index
                        ? 'bg-green-500'
                        : index === currentSegment.index
                          ? 'bg-blue-600'
                          : 'bg-gray-200'
                    }`}
                  />
                ))}
              </div>
            )}

            <p className="text-xs text-gray-500 text-center">
              Общая запись: {formatSeconds(recordSecondsLeft)} осталось. Паузы и перезапуска во время ответа нет.
            </p>
          </>
        )}

        {phase === 'idle' && (
          <div className="flex flex-col items-center gap-4">
            <p className="text-gray-500 text-center">
              Когда будете готовы, нажмите кнопку ниже. Сначала браузер попросит доступ к микрофону.
            </p>
            <button
              onClick={() => void handleStart()}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
            >
              {prepSeconds > 0 ? 'Начать подготовку' : 'Начать запись'}
            </button>

            <div className="w-full max-w-xl border-t border-gray-200 pt-5 mt-2">
              <p className="text-sm font-medium text-gray-700 text-center mb-3">
                Или загрузите готовую аудиозапись для этого задания
              </p>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-center">
                <label className="cursor-pointer rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 text-center">
                  Выбрать файл
                  <input
                    type="file"
                    accept={ACCEPTED_AUDIO_TYPES}
                    onChange={handleFileChange}
                    className="sr-only"
                  />
                </label>
                <button
                  type="button"
                  onClick={() => void handleUploadFile()}
                  disabled={!selectedAudioFile}
                  className="rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-300 disabled:text-gray-500"
                >
                  Отправить файл на проверку
                </button>
              </div>
              {selectedAudioFile && (
                <p className="mt-3 text-center text-xs text-gray-500">
                  Выбран файл: <span className="font-medium text-gray-700">{selectedAudioFile.name}</span> ({formatFileSize(selectedAudioFile.size)})
                </p>
              )}
              <p className="mt-2 text-center text-xs text-gray-400">
                Поддерживаются mp3, wav, m4a/mp4, webm, ogg. Максимум 16 МБ.
              </p>
            </div>
          </div>
        )}

        {phase === 'checking' && (
          <div className="flex flex-col items-center gap-3">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
            <p className="text-gray-500">Проверяем доступ к микрофону...</p>
          </div>
        )}

        {phase === 'starting' && (
          <div className="flex flex-col items-center gap-3">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
            <p className="text-gray-500">Запускаем запись...</p>
          </div>
        )}

        {phase === 'submitting' && (
          <div className="flex flex-col items-center gap-3">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
            <p className="text-gray-500">Анализируем ваш ответ...</p>
          </div>
        )}

        {(recorderError || submitError) && (
          <p className="text-red-500 text-sm text-center">
            {recorderError || submitError}
          </p>
        )}
      </div>
    </div>
  );
}
