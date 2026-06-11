'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { TASK_CONFIG, TaskType } from '@/config/tasks';
import { useTimer } from '@/hooks/useTimer';
import { useRecorder } from '@/hooks/useRecorder';
import Timer from '@/components/exam/Timer';
import TaskDisplay from '@/components/exam/TaskDisplay';

type Phase = 'idle' | 'preparing' | 'recording' | 'submitting' | 'done';

// Demo question for testing — we'll replace this with real questions from the backend later
const DEMO_QUESTION = {
  task2: {
    promptText: `Вы хотите узнать больше о жизни в другой стране. Задайте 5 вопросов своему другу, который недавно переехал за границу.

Спросите о:
- городе, в котором он живёт
- работе или учёбе
- местной еде
- свободном времени
- планах на будущее`,
    imageUrl: undefined,
  },
};

export default function ExamPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params.taskId as TaskType;
  const task = TASK_CONFIG[taskId];

  const [phase, setPhase] = useState<Phase>('idle');
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { isRecording, audioBlob, error: recorderError, start: startRecording, stop: stopRecording } = useRecorder();

  const onPrepComplete = useCallback(() => {
    setPhase('recording');
    startRecording();
    recordTimer.start();
  }, []);

  const onRecordComplete = useCallback(() => {
    stopRecording();
    setPhase('submitting');
  }, []);

  const prepTimer = useTimer(task?.prepSeconds ?? 0, onPrepComplete);
  const recordTimer = useTimer(task?.recordSeconds ?? 0, onRecordComplete);

  // Submit when audioBlob is ready and we are in submitting phase
  useEffect(() => {
    if (phase === 'submitting' && audioBlob) {
      submitAudio(audioBlob);
    }
  }, [phase, audioBlob]);

  const submitAudio = async (blob: Blob) => {
    setSubmitError(null);
    try {
      const formData = new FormData();
      formData.append('audio', blob, 'recording.webm');
      formData.append('task_type', taskId);
      formData.append('prompt_text', DEMO_QUESTION[taskId as keyof typeof DEMO_QUESTION]?.promptText ?? '');

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/evaluate`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Ошибка при отправке записи');

      const data = await res.json();
      router.push(`/results/${data.submission_id}?data=${encodeURIComponent(JSON.stringify(data))}`);
    } catch (err) {
      setSubmitError('Не удалось отправить запись. Попробуйте ещё раз.');
      setPhase('idle');
    }
  };

  const handleStart = () => {
    if (task.prepSeconds > 0) {
      setPhase('preparing');
      prepTimer.start();
    } else {
      setPhase('recording');
      startRecording();
      recordTimer.start();
    }
  };

  if (!task) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <p className="text-red-500">Неверный тип задания.</p>
      </div>
    );
  }

  const question = DEMO_QUESTION[taskId as keyof typeof DEMO_QUESTION];

  return (
    <div className="max-w-3xl mx-auto p-6 min-h-screen">
      <TaskDisplay
        title={task.title}
        description={task.description}
        promptText={question?.promptText ?? 'Задание загружается...'}
        imageUrl={question?.imageUrl}
      />

      <div className="bg-white border border-gray-200 rounded-lg p-8 flex flex-col items-center gap-6">
        {/* Preparation phase */}
        {phase === 'preparing' && (
          <Timer
            display={prepTimer.display}
            label="Время на подготовку"
            isRunning={prepTimer.isRunning}
          />
        )}

        {/* Recording phase */}
        {phase === 'recording' && (
          <Timer
            display={recordTimer.display}
            label="Время ответа"
            isRunning={recordTimer.isRunning}
            isRecording={true}
          />
        )}

        {/* Idle state */}
        {phase === 'idle' && (
          <div className="flex flex-col items-center gap-4">
            <p className="text-gray-500 text-center">
              Когда будете готовы, нажмите кнопку ниже чтобы начать подготовку.
            </p>
            <button
              onClick={handleStart}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
            >
              Начать подготовку
            </button>
          </div>
        )}

        {/* Submitting state */}
        {phase === 'submitting' && (
          <div className="flex flex-col items-center gap-3">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
            <p className="text-gray-500">Анализируем ваш ответ...</p>
          </div>
        )}

        {/* Errors */}
        {(recorderError || submitError) && (
          <p className="text-red-500 text-sm text-center">
            {recorderError || submitError}
          </p>
        )}
      </div>
    </div>
  );
}
