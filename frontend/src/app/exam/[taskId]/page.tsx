'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { TASK_CONFIG, TaskType, RecordingSegment } from '@/config/tasks';
import { DEFAULT_CURRENCY_LABEL, DEFAULT_TASK_CREDIT_COST, BillingPublicInfo } from '@/config/billing';
import { getAuthHeaders } from '@/config/auth';
import { useTimer } from '@/hooks/useTimer';
import { useRecorder } from '@/hooks/useRecorder';
import Timer from '@/components/exam/Timer';
import TaskDisplay from '@/components/exam/TaskDisplay';

type Phase = 'idle' | 'checking' | 'preparing' | 'starting' | 'listening' | 'recording' | 'submitting';

const MAX_AUDIO_BYTES = 16 * 1024 * 1024;
const ACCEPTED_AUDIO_TYPES = 'audio/webm,audio/ogg,audio/mpeg,audio/mp3,audio/mp4,audio/m4a,audio/x-m4a,audio/aac,audio/wav,audio/x-wav,.webm,.ogg,.mp3,.mp4,.m4a,.aac,.wav';
const ACCEPTED_AUDIO_EXTENSIONS = ['webm', 'ogg', 'mp3', 'mp4', 'm4a', 'aac', 'wav'];

interface TaskAudioConfig {
  intro?: string;
  startCue?: string;
  questionCues?: readonly string[];
  end?: string;
}

interface DemoQuestion {
  id?: string;
  taskType?: TaskType;
  promptText: string;
  gradingPromptText?: string;
  imageUrl?: string;
  imageUrls?: readonly string[];
  imageCaptions?: readonly string[];
  task2Prompts?: readonly string[];
  interviewerIntro?: string;
  interviewQuestions?: readonly string[];
  audio?: TaskAudioConfig;
}

interface BackendQuestionAudio {
  intro?: string | null;
  start_cue?: string | null;
  question_cues?: string[];
  end?: string | null;
}

interface BackendQuestion {
  id: string;
  task_type: TaskType;
  prompt_text: string;
  grading_prompt_text?: string | null;
  image_url?: string | null;
  image_urls?: string[];
  image_captions?: string[];
  task2_prompts?: string[];
  interviewer_intro?: string | null;
  interview_questions?: string[];
  audio?: BackendQuestionAudio | null;
}

function mapBackendQuestion(question: BackendQuestion): DemoQuestion {
  return {
    id: question.id,
    taskType: question.task_type,
    promptText: question.prompt_text,
    gradingPromptText: question.grading_prompt_text ?? undefined,
    imageUrl: question.image_url ?? undefined,
    imageUrls: question.image_urls ?? [],
    imageCaptions: question.image_captions ?? [],
    task2Prompts: question.task2_prompts ?? [],
    interviewerIntro: question.interviewer_intro ?? undefined,
    interviewQuestions: question.interview_questions ?? [],
    audio: question.audio
      ? {
          intro: question.audio.intro ?? undefined,
          startCue: question.audio.start_cue ?? undefined,
          questionCues: question.audio.question_cues ?? [],
          end: question.audio.end ?? undefined,
        }
      : undefined,
  };
}

function makeSvgDataUri(title: string, subtitle: string, background: string, accent: string) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420">
    <rect width="640" height="420" fill="${background}"/>
    <circle cx="520" cy="80" r="46" fill="${accent}" opacity="0.35"/>
    <rect x="70" y="255" width="500" height="72" rx="18" fill="#ffffff" opacity="0.88"/>
    <circle cx="210" cy="205" r="42" fill="#ffffff" opacity="0.82"/>
    <circle cx="315" cy="190" r="46" fill="#ffffff" opacity="0.82"/>
    <circle cx="425" cy="210" r="40" fill="#ffffff" opacity="0.82"/>
    <rect x="175" y="240" width="285" height="44" rx="18" fill="${accent}" opacity="0.72"/>
    <text x="320" y="350" text-anchor="middle" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#1f2937">${title}</text>
    <text x="320" y="382" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#4b5563">${subtitle}</text>
  </svg>`;

  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

const TASK4_IMAGE_1 = makeSvgDataUri('Photo 1', 'Family picnic in a park', '#dcfce7', '#22c55e');
const TASK4_IMAGE_2 = makeSvgDataUri('Photo 2', 'Teenagers watching a film at home', '#dbeafe', '#3b82f6');

const TASK3_INTERVIEW_QUESTIONS = [
  'In what region do you live? Do you live in a big city, a town or in a village?',
  'Do you live in a flat or in a house? What is it like?',
  'What would you like to change about your flat or house? Why?',
  'What do you like and dislike about your neighbourhood?',
  'What kind of housing would you like to have in the future?',
] as const;

const TASK3_INTERVIEW_INTRO = "Hello! It's Teenagers Round the World Channel. Our guest today is a teenager from Russia and we are going to discuss teenagers' attitude to their accommodation. Please answer five questions. So, let's get started.";

const DEMO_QUESTIONS: Record<TaskType, DemoQuestion> = {
  task1: {
    promptText: `Task 1. You are going to read the text aloud. You have 1.5 minutes to read the text silently, then be ready to read it aloud. Remember that you will not have more than 1.5 minutes for reading aloud.

Snowflakes are ice crystals which fall through the Earth's atmosphere as snow. People like to think that every snowflake has a unique shape. However, it is not true. While snowflakes may look different, they can still be classified into eight groups and about eighty different variants. Some scientists have done a lot of research into making a kind of catalogue of snowflakes.

The most typical patterns for a snowflake are needles, columns, plates and rimes. The shape and the pattern of a snowflake largely depend on the weather conditions. The study of snowflakes has identified that long, thin needle-like ice crystals form at around zero, while a lower temperature will lead to very flat crystals. Further changes in temperature as a snowflake falls determine more complicated shapes of snowflakes. The size of a snowflake also depends on the air temperature.`,
    audio: {
      intro: '/audio/ege/task1/intro.mp3',
    },
  },
  task2: {
    promptText: `Task 2. Study the advertisement.

THE BEST CLINIC IN TOWN!

You are considering visiting the clinic and now you would like to get more information. In 1.5 minutes you are to ask four direct questions to find out about the following:

1) location
2) public transport
3) dentist
4) family discounts

You have 20 seconds to ask each question.`,
    task2Prompts: ['location', 'public transport', 'dentist', 'family discounts'],
    audio: {
      intro: '/audio/ege/task2/variant01/intro.mp3',
      questionCues: [
        '/audio/ege/task2/variant01/q1.mp3',
        '/audio/ege/task2/variant01/q2.mp3',
        '/audio/ege/task2/variant01/q3.mp3',
        '/audio/ege/task2/variant01/q4.mp3',
      ],
    },
  },
  task3: {
    promptText: `Task 3. You are going to give an interview. You have to answer five questions.

Give full answers to the questions: 2–3 sentences.

Remember that you have 40 seconds to answer each question.

The questions are played by the interviewer and are not shown on the screen, closer to the real exam format.`,
    gradingPromptText: `Task 3. You are going to give an interview. You have to answer five questions. Give full answers to the questions: 2–3 sentences. Remember that you have 40 seconds to answer each question.

Interviewer intro:
${TASK3_INTERVIEW_INTRO}

Questions:
${TASK3_INTERVIEW_QUESTIONS.map((question, index) => `${index + 1}) ${question}`).join('\n')}`,
    interviewerIntro: TASK3_INTERVIEW_INTRO,
    interviewQuestions: TASK3_INTERVIEW_QUESTIONS,
    audio: {
      intro: '/audio/ege/task3/variant01/intro.mp3',
      questionCues: [
        '/audio/ege/task3/variant01/q1.mp3',
        '/audio/ege/task3/variant01/q2.mp3',
        '/audio/ege/task3/variant01/q3.mp3',
        '/audio/ege/task3/variant01/q4.mp3',
        '/audio/ege/task3/variant01/q5.mp3',
      ],
      end: '/audio/ege/common/interview_end.mp3',
    },
  },
  task4: {
    promptText: `Task 4. Imagine that you and your friend are doing a school project “Ideal weekend”. You have found two photos to illustrate it but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.

In 2.5 minutes be ready to:

• explain the choice of the illustrations for the project by briefly describing them and noting the differences;
• mention the advantages (1–2) of the two ways to spend the weekend;
• mention the disadvantages (1–2) of the two ways to spend the weekend;
• express your opinion on the subject of the project — say which way of spending the weekend presented in the pictures you prefer and why.

You will speak for not more than 3 minutes: 12–15 sentences. You have to talk continuously.`,
    gradingPromptText: `Task 4. Imagine that you and your friend are doing a school project “Ideal weekend”. You have found two photos to illustrate it but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.

Photo 1: a family is having a picnic in a park.
Photo 2: two teenagers are watching a film at home.

In 2.5 minutes be ready to:
- explain the choice of the illustrations for the project by briefly describing them and noting the differences;
- mention the advantages (1–2) of the two ways to spend the weekend;
- mention the disadvantages (1–2) of the two ways to spend the weekend;
- express your opinion on the subject of the project — say which way of spending the weekend presented in the pictures you prefer and why.

You will speak for not more than 3 minutes: 12–15 sentences. You have to talk continuously.`,
    imageUrls: [TASK4_IMAGE_1, TASK4_IMAGE_2],
    imageCaptions: ['Photo 1', 'Photo 2'],
    audio: {
      intro: '/audio/ege/task4/variant01/intro.mp3',
      startCue: '/audio/ege/common/start_speaking.mp3',
    },
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

function delay(milliseconds: number) {
  return new Promise<void>(resolve => {
    window.setTimeout(resolve, milliseconds);
  });
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

function getAudioContextClass() {
  return window.AudioContext || (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
}

async function playBeep() {
  const AudioContextClass = getAudioContextClass();
  if (!AudioContextClass) return;

  const audioContext = new AudioContextClass();
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();

  oscillator.type = 'sine';
  oscillator.frequency.value = 880;
  gain.gain.value = 0.08;

  oscillator.connect(gain);
  gain.connect(audioContext.destination);
  oscillator.start();
  oscillator.stop(audioContext.currentTime + 0.16);

  await delay(220);
  await audioContext.close();
}

function playAudioFile(src: string) {
  return new Promise<boolean>(resolve => {
    const audio = new Audio(src);
    let resolved = false;

    const finish = (ok: boolean) => {
      if (!resolved) {
        resolved = true;
        resolve(ok);
      }
    };

    audio.preload = 'auto';
    audio.onended = () => finish(true);
    audio.onerror = () => finish(false);

    audio.play().catch(() => finish(false));
  });
}

function speakText(text: string) {
  return new Promise<boolean>(resolve => {
    if (!('speechSynthesis' in window) || typeof SpeechSynthesisUtterance === 'undefined') {
      resolve(false);
      return;
    }

    let resolved = false;
    const utterance = new SpeechSynthesisUtterance(text);
    const fallbackTimeout = window.setTimeout(() => {
      if (!resolved) {
        resolved = true;
        resolve(false);
      }
    }, Math.max(6000, text.length * 95));

    utterance.lang = 'en-US';
    utterance.rate = 0.92;
    utterance.pitch = 1;
    utterance.onend = () => {
      if (!resolved) {
        resolved = true;
        window.clearTimeout(fallbackTimeout);
        resolve(true);
      }
    };
    utterance.onerror = () => {
      if (!resolved) {
        resolved = true;
        window.clearTimeout(fallbackTimeout);
        resolve(false);
      }
    };

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  });
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
  const fallbackQuestion = taskId ? DEMO_QUESTIONS[taskId] : null;
  const prepSeconds = task?.prepSeconds ?? 0;
  const recordingSegments = task?.recordingSegments ?? [];
  const recordDuration = recordingSegments.reduce((sum, segment) => sum + segment.seconds, 0);
  const isTask2 = taskId === 'task2';
  const isTask3 = taskId === 'task3';
  const isSegmentedAudioTask = isTask2 || isTask3;

  const [phase, setPhase] = useState<Phase>('idle');
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [selectedAudioFile, setSelectedAudioFile] = useState<File | null>(null);
  const [loadedQuestion, setLoadedQuestion] = useState<DemoQuestion | null>(null);
  const [questionLoadError, setQuestionLoadError] = useState<string | null>(null);
  const [isQuestionLoading, setIsQuestionLoading] = useState(false);
  const [taskCreditCost, setTaskCreditCost] = useState(DEFAULT_TASK_CREDIT_COST);
  const [currencyLabel, setCurrencyLabel] = useState(DEFAULT_CURRENCY_LABEL);
  const [currentAudioPromptIndex, setCurrentAudioPromptIndex] = useState(0);
  const [fallbackPromptText, setFallbackPromptText] = useState<string | null>(null);
  const [activeAudioTitle, setActiveAudioTitle] = useState('Звучит аудио');
  const [activeAudioDescription, setActiveAudioDescription] = useState('Слушайте аудио. После сигнала начнётся запись ответа.');

  const question = loadedQuestion ?? fallbackQuestion;

  const startRecordingPhaseRef = useRef<(() => Promise<void>) | null>(null);
  const recordTimerCompleteRef = useRef<(() => Promise<void>) | null>(null);
  const errorMessageRef = useRef<HTMLParagraphElement | null>(null);

  const {
    isRecording,
    error: recorderError,
    start: startRecording,
    pause: pauseRecording,
    resume: resumeRecording,
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
    void recordTimerCompleteRef.current?.();
  });

  async function playPromptAudio({
    src,
    fallbackText,
    title,
    description,
    showFallbackText = false,
    fallbackDelayMs = 2500,
  }: {
    src?: string;
    fallbackText?: string;
    title: string;
    description: string;
    showFallbackText?: boolean;
    fallbackDelayMs?: number;
  }) {
    setActiveAudioTitle(title);
    setActiveAudioDescription(description);
    setFallbackPromptText(null);
    setPhase('listening');

    if (src) {
      const playedStaticAudio = await playAudioFile(src);
      if (playedStaticAudio) return true;
    }

    if (fallbackText) {
      const playedBrowserTts = await speakText(fallbackText);
      if (playedBrowserTts) return false;

      if (showFallbackText) setFallbackPromptText(fallbackText);
      await delay(fallbackDelayMs);
    }

    return false;
  }

  async function submitAudio(blob: Blob) {
    if (!taskId || !question) return;

    setSubmitError(null);

    try {
      const formData = new FormData();
      formData.append('audio', blob, getAudioFilename(blob));
      formData.append('task_type', taskId);
      formData.append('source', blob instanceof File ? 'uploaded' : 'recorded');
      if (question.id) formData.append('question_id', question.id);
      formData.append('prompt_text', question.gradingPromptText ?? question.promptText);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
      const response = await fetch(`${apiUrl}/evaluate`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        const errorText = await readApiError(response);
        throw new Error(`Не удалось отправить запись: ${errorText}`);
      }

      const data = await response.json();
      router.push(`/results/${data.submission_id}`);
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

  async function beginSegmentedAnswer(seconds: number) {
    const resumed = resumeRecording();

    if (!resumed) {
      setSubmitError('Не удалось возобновить запись ответа. Попробуйте ещё раз.');
      setPhase('idle');
      return;
    }

    setPhase('recording');
    startRecordTimer(seconds);
  }

  async function playTask2Cue(index: number) {
    if (!question?.task2Prompts) return;

    const pointText = question.task2Prompts[index];
    const fallbackText = `Question ${index + 1}. Ask about ${pointText}.`;
    setCurrentAudioPromptIndex(index);
    pauseRecording();

    await playPromptAudio({
      src: question.audio?.questionCues?.[index],
      fallbackText,
      title: `Question ${index + 1} / ${question.task2Prompts.length}`,
      description: 'Слушайте пункт, о котором нужно задать прямой вопрос. После сигнала начнётся запись на 20 секунд.',
      fallbackDelayMs: 1800,
    });

    await playBeep();
    await beginSegmentedAnswer(20);
  }

  async function playTask3Question(index: number) {
    if (!question?.interviewQuestions) return;

    const questionText = question.interviewQuestions[index];
    setCurrentAudioPromptIndex(index);
    pauseRecording();

    await playPromptAudio({
      src: question.audio?.questionCues?.[index],
      fallbackText: `Question ${index + 1}. ${questionText}`,
      title: `Question ${index + 1} / ${question.interviewQuestions.length}`,
      description: 'Слушайте вопрос интервьюера. После сигнала начнётся запись ответа на 40 секунд.',
      showFallbackText: true,
      fallbackDelayMs: 6000,
    });

    await playBeep();
    await beginSegmentedAnswer(40);
  }

  async function finishSegmentedRecording() {
    stopRecordTimer();
    pauseRecording();

    if (isTask3 && question?.audio?.end) {
      await playPromptAudio({
        src: question.audio.end,
        fallbackText: 'Thank you very much for your interview.',
        title: 'Интервью завершено',
        description: 'Слушайте завершающую фразу. После этого ответ будет отправлен на проверку.',
        fallbackDelayMs: 1800,
      });
    }

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

  async function completeSegmentedAnswer() {
    stopRecordTimer();
    pauseRecording();

    const nextIndex = currentAudioPromptIndex + 1;
    const questionCount = isTask2
      ? question?.task2Prompts?.length ?? 0
      : question?.interviewQuestions?.length ?? 0;

    if (nextIndex < questionCount) {
      if (isTask2) await playTask2Cue(nextIndex);
      else await playTask3Question(nextIndex);
      return;
    }

    await finishSegmentedRecording();
  }

  async function handleRecordTimerComplete() {
    if (isSegmentedAudioTask && phase === 'recording') {
      await completeSegmentedAnswer();
      return;
    }

    await finishRecording();
  }

  async function startSegmentedAudioFlow() {
    if (!question || (!question.task2Prompts?.length && !question.interviewQuestions?.length)) return;

    setSubmitError(null);
    setCurrentAudioPromptIndex(0);
    setFallbackPromptText(null);
    resetRecordTimer(isTask2 ? 20 : 40);
    setPhase('starting');

    const started = await startRecording();

    if (!started) {
      setPhase('idle');
      return;
    }

    pauseRecording();

    if (isTask2) await playTask2Cue(0);
    else await playTask3Question(0);
  }

  async function startRecordingPhase() {
    if (!task || !question || recordDuration <= 0) return;

    if (isSegmentedAudioTask) {
      await startSegmentedAudioFlow();
      return;
    }

    setSubmitError(null);
    resetRecordTimer(recordDuration);
    setPhase('starting');

    if (question.audio?.startCue) {
      await playPromptAudio({
        src: question.audio.startCue,
        fallbackText: taskId === 'task1' ? 'Now start reading, please.' : 'Now start speaking, please.',
        title: taskId === 'task1' ? 'Начинайте чтение' : 'Начинайте ответ',
        description: 'После сигнала начнётся запись ответа.',
        fallbackDelayMs: 1200,
      });
    }

    await playBeep();

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
    recordTimerCompleteRef.current = handleRecordTimerComplete;
  });

  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadDemoQuestion() {
      if (!taskId) return;

      setIsQuestionLoading(true);
      setQuestionLoadError(null);

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
        const response = await fetch(`${apiUrl}/questions/demo/${taskId}`, {
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error(`Backend вернул ошибку ${response.status}`);
        }

        const data = await response.json() as BackendQuestion;
        if (cancelled) return;

        setLoadedQuestion(mapBackendQuestion(data));
      } catch (caughtError) {
        console.warn('Could not load demo question from backend, using frontend fallback', caughtError);
        if (!cancelled) {
          setLoadedQuestion(null);
          setQuestionLoadError('Не удалось загрузить задание с backend. Используется локальная демо-версия.');
        }
      } finally {
        if (!cancelled) setIsQuestionLoading(false);
      }
    }

    void loadDemoQuestion();

    return () => {
      cancelled = true;
    };
  }, [taskId]);

  useEffect(() => {
    if (!recorderError && !submitError) return;

    const timeoutId = window.setTimeout(() => {
      errorMessageRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
      errorMessageRef.current?.focus({ preventScroll: true });
    }, 50);

    return () => window.clearTimeout(timeoutId);
  }, [recorderError, submitError]);

  useEffect(() => {
    let cancelled = false;

    async function loadBillingInfo() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
        const response = await fetch(`${apiUrl}/billing/public`, {
          credentials: 'include',
        });
        if (!response.ok) return;

        const data = await response.json() as BillingPublicInfo;
        if (cancelled) return;

        setTaskCreditCost({
          ...DEFAULT_TASK_CREDIT_COST,
          ...data.task_credit_cost,
        });
        setCurrencyLabel(data.currency_label || DEFAULT_CURRENCY_LABEL);
      } catch (caughtError) {
        console.warn('Could not load billing info, using defaults', caughtError);
      }
    }

    void loadBillingInfo();

    return () => {
      cancelled = true;
    };
  }, []);

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
    resetRecordTimer(isTask2 ? 20 : isTask3 ? 40 : recordDuration);
    setSubmitError(null);

    // Play the task instruction immediately after the user's click and before the prep timer.
    // This is closer to the exam flow and avoids browser autoplay restrictions after async mic checks.
    if (question.audio?.intro) {
      await playPromptAudio({
        src: question.audio.intro,
        fallbackText: question.promptText.split('\n\n')[0],
        title: 'Инструкция задания',
        description: 'Слушайте инструкцию. После неё начнётся подготовка или запись.',
        fallbackDelayMs: 2500,
      });
    }

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

  if (!task || !taskId) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <p className="text-red-500">Неверный тип задания.</p>
      </div>
    );
  }

  if (isQuestionLoading && !question) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-gray-500">
          Загружаем задание...
        </div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <p className="text-red-500">Не удалось загрузить задание.</p>
      </div>
    );
  }

  const secondsElapsed = phase === 'recording' ? recordDuration - recordSecondsLeft : 0;
  const currentSegment = isSegmentedAudioTask
    ? {
        index: currentAudioPromptIndex,
        segment: recordingSegments[currentAudioPromptIndex] ?? recordingSegments[0],
        secondsLeft: recordSecondsLeft,
      }
    : getCurrentSegment(recordingSegments, secondsElapsed);
  const segmentDisplay = currentSegment ? formatSeconds(currentSegment.secondsLeft) : formatSeconds(recordSecondsLeft);
  const segmentLabel = currentSegment
    ? recordingSegments.length > 1
      ? `${currentSegment.segment.label} из ${recordingSegments.length}`
      : 'Время ответа'
    : 'Время ответа';
  const task2CurrentPrompt = taskId === 'task2' && currentSegment
    ? question.task2Prompts?.[currentSegment.index]
    : null;
  const currentTaskCreditCost = taskCreditCost[taskId];

  return (
    <div className="max-w-3xl mx-auto p-6 min-h-screen bg-gray-50">
      <TaskDisplay
        title={task.title}
        description={task.description}
        promptText={question.promptText}
        imageUrl={question.imageUrl}
        imageUrls={question.imageUrls}
        imageCaptions={question.imageCaptions}
      />

      {questionLoadError && (
        <div className="mb-6 rounded-lg border border-yellow-200 bg-yellow-50 px-4 py-3 text-sm text-yellow-900">
          {questionLoadError}
        </div>
      )}

      <div className="mb-6 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-900">
        <span className="font-semibold">Стоимость AI-проверки:</span>{' '}
        {currentTaskCreditCost} {currencyLabel}. Сейчас демо-проверка доступна без списания; после запуска аккаунтов стоимость можно будет менять в backend config.
      </div>

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

        {phase === 'listening' && (
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="animate-pulse rounded-full h-12 w-12 bg-blue-100 flex items-center justify-center text-2xl" aria-hidden="true">
              🎧
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                {activeAudioTitle}
              </p>
              <p className="text-sm text-gray-500 max-w-md mt-2">
                {activeAudioDescription}
              </p>
            </div>
            {fallbackPromptText && (
              <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-left text-sm text-yellow-900 max-w-xl">
                <p className="font-semibold mb-1">Не удалось надёжно проиграть аудио. Текст показан как fallback:</p>
                <p>{fallbackPromptText}</p>
              </div>
            )}
          </div>
        )}

        {phase === 'recording' && (
          <>
            <Timer
              display={segmentDisplay}
              label={segmentLabel}
              isRunning={isRecordTimerRunning}
              isRecording={isRecording}
            />

            {task2CurrentPrompt && (
              <div className="rounded-lg border border-blue-100 bg-blue-50 px-5 py-3 text-center">
                <p className="text-xs font-medium uppercase tracking-wide text-blue-600">Спросите о</p>
                <p className="text-lg font-semibold text-blue-950">{task2CurrentPrompt}</p>
              </div>
            )}

            {isTask3 && (
              <p className="text-sm text-gray-500 text-center max-w-md">
                Отвечайте на услышанный вопрос полным ответом: 2–3 предложения. Текст вопроса на экзамене не показывается.
              </p>
            )}

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

            {!isSegmentedAudioTask && (
              <p className="text-xs text-gray-500 text-center">
                Общая запись: {formatSeconds(recordSecondsLeft)} осталось. Паузы и перезапуска во время ответа нет.
              </p>
            )}
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
              {prepSeconds > 0 ? 'Начать подготовку' : isTask3 ? 'Начать интервью' : 'Начать запись'}
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
          <p
            ref={errorMessageRef}
            role="alert"
            tabIndex={-1}
            className="text-red-500 text-sm text-center outline-none"
          >
            {recorderError || submitError}
          </p>
        )}
      </div>
    </div>
  );
}
