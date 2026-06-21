'use client';

import Link from 'next/link';
import { useParams, useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';
import { DEFAULT_FREE_REGISTERED_CREDITS } from '@/config/billing';
import { TASK_CONFIG, TaskType } from '@/config/tasks';

interface CriterionScore {
  score: number;
  max_score: number;
  feedback: string;
}

interface GradeResult {
  criteria: Record<string, CriterionScore>;
  total: number;
  max_total: number;
  summary: string;
}

interface SubmissionData {
  submission_id: string;
  task_type?: string;
  transcript: string;
  grade: GradeResult;
}

const CRITERION_LABELS: Record<string, string> = {
  phonetics: 'Фонетическая сторона речи',
  questions: 'Вопросы',
  question_1: 'Вопрос 1',
  question_2: 'Вопрос 2',
  question_3: 'Вопрос 3',
  question_4: 'Вопрос 4',
  answer_1: 'Ответ 1',
  answer_2: 'Ответ 2',
  answer_3: 'Ответ 3',
  answer_4: 'Ответ 4',
  answer_5: 'Ответ 5',
  content: 'Решение коммуникативной задачи',
  organisation: 'Организация высказывания',
  language: 'Языковое оформление',
};

function parseSubmissionData(raw: string): SubmissionData | null {
  try {
    return JSON.parse(raw) as SubmissionData;
  } catch {
    try {
      return JSON.parse(decodeURIComponent(raw)) as SubmissionData;
    } catch {
      return null;
    }
  }
}

function getRetryTask(taskType: string | undefined): TaskType {
  return taskType && taskType in TASK_CONFIG ? (taskType as TaskType) : 'task2';
}

function getSubmissionId(param: string | string[] | undefined) {
  if (Array.isArray(param)) return param[0];
  return param;
}

function ResultsContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const submissionId = getSubmissionId(params.submissionId);
  const legacyRawData = searchParams.get('data');
  const initialLegacyData = legacyRawData ? parseSubmissionData(legacyRawData) : null;

  const [data, setData] = useState<SubmissionData | null>(initialLegacyData);
  const [isLoading, setIsLoading] = useState(!legacyRawData && Boolean(submissionId));
  const [error, setError] = useState<string | null>(
    legacyRawData && !initialLegacyData
      ? 'Не удалось прочитать данные результата из URL.'
      : !legacyRawData && !submissionId
        ? 'ID результата не найден.'
        : null,
  );

  useEffect(() => {
    if (legacyRawData) return;

    if (!submissionId) return;

    let cancelled = false;

    async function loadSubmission() {
      setIsLoading(true);
      setError(null);

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
        const response = await fetch(`${apiUrl}/submissions/${submissionId}`);

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('Результат не найден. Если backend был перезапущен, временный результат мог исчезнуть.');
          }
          throw new Error(`Backend вернул ошибку ${response.status}.`);
        }

        const result = await response.json() as SubmissionData;
        if (!cancelled) setData(result);
      } catch (caughtError) {
        console.error(caughtError);
        if (!cancelled) {
          setError(caughtError instanceof Error ? caughtError.message : 'Не удалось загрузить результат.');
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void loadSubmission();

    return () => {
      cancelled = true;
    };
  }, [legacyRawData, submissionId]);

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-gray-500">
          Загружаем результат...
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-700">
          <h1 className="font-semibold">Данные результата не найдены</h1>
          <p className="mt-2 text-sm leading-6">{error ?? 'Не удалось загрузить данные результата.'}</p>
          <div className="mt-5">
            <Link href="/" className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-red-700 ring-1 ring-red-200 hover:bg-red-50">
              На главную
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { transcript, grade } = data;
  const retryTask = getRetryTask(data.task_type);

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Результаты</h1>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6 flex items-center justify-between">
        <div>
          <p className="text-sm text-blue-600 font-medium uppercase tracking-wide">Итоговый балл</p>
          <p className="text-4xl font-bold text-blue-900 mt-1">
            {grade.total} / {grade.max_total}
          </p>
        </div>
        <div className="text-5xl" aria-hidden="true">
          {grade.total === grade.max_total ? '🏆' : grade.total >= grade.max_total / 2 ? '👍' : '📚'}
        </div>
      </div>

      <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 mb-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-semibold text-blue-950">Хотите больше заданий?</h2>
            <p className="mt-2 text-sm leading-6 text-blue-800">
              Это фиксированное демо-задание. После регистрации планируется стартовый баланс {DEFAULT_FREE_REGISTERED_CREDITS} кредитов, больше вариантов, история попыток и покупка дополнительных AI-проверок.
            </p>
          </div>
          <div className="flex shrink-0 gap-2">
            <Link
              href="/register"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
            >
              Зарегистрироваться
            </Link>
            <Link
              href="/login"
              className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-blue-700 ring-1 ring-blue-200 transition-colors hover:bg-blue-50"
            >
              Войти
            </Link>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="font-semibold text-gray-900 mb-2">Общий отзыв</h2>
        <p className="text-gray-700 leading-relaxed">{grade.summary}</p>
      </div>

      <div className="space-y-4 mb-6">
        <h2 className="font-semibold text-gray-900">Разбор по критериям</h2>
        {Object.entries(grade.criteria).map(([key, criterion]) => (
          <div key={key} className="bg-white border border-gray-200 rounded-lg p-5">
            <div className="flex justify-between items-center mb-2 gap-4">
              <span className="font-medium text-gray-800">
                {CRITERION_LABELS[key] ?? key.replace(/_/g, ' ')}
              </span>
              <span className={`font-bold text-lg ${
                criterion.score === criterion.max_score
                  ? 'text-green-600'
                  : criterion.score > 0
                    ? 'text-yellow-600'
                    : 'text-red-600'
              }`}>
                {criterion.score} / {criterion.max_score}
              </span>
            </div>
            <p className="text-gray-600 text-sm leading-relaxed">{criterion.feedback}</p>
          </div>
        ))}
      </div>

      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="font-semibold text-gray-900 mb-2">Ваш ответ: транскрипция</h2>
        <p className="text-gray-600 text-sm leading-relaxed italic whitespace-pre-wrap">{transcript}</p>
      </div>

      <div className="flex gap-4">
        <Link
          href={`/exam/${retryTask}`}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
        >
          Попробовать ещё раз
        </Link>
        <Link
          href="/"
          className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold px-6 py-3 rounded-lg transition-colors"
        >
          На главную
        </Link>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<div className="max-w-3xl mx-auto p-6">Загрузка...</div>}>
      <ResultsContent />
    </Suspense>
  );
}
