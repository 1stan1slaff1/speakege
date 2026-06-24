'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { clearStoredToken, getAuthHeaders, getStoredToken } from '@/config/auth';
import { TASK_CONFIG, TaskType } from '@/config/tasks';

interface AttemptHistoryItem {
  id: string;
  question_id?: string | null;
  task_type: string;
  status: string;
  source: string;
  total_score?: number | null;
  max_score?: number | null;
  credit_cost: number;
  created_at: string;
  completed_at?: string | null;
}

function getTaskTitle(taskType: string) {
  return taskType in TASK_CONFIG
    ? TASK_CONFIG[taskType as TaskType].title
    : taskType;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

function sourceLabel(source: string) {
  if (source === 'uploaded') return 'Загруженный файл';
  if (source === 'recorded') return 'Запись в браузере';
  return source;
}

function statusLabel(status: string) {
  if (status === 'completed') return 'Завершено';
  if (status === 'processing') return 'В обработке';
  if (status === 'failed') return 'Ошибка';
  return status;
}

function statusClassName(status: string) {
  if (status === 'completed') return 'bg-green-50 text-green-700 ring-green-100';
  if (status === 'processing') return 'bg-blue-50 text-blue-700 ring-blue-100';
  if (status === 'failed') return 'bg-red-50 text-red-700 ring-red-100';
  return 'bg-gray-50 text-gray-700 ring-gray-100';
}

export default function HistoryPage() {
  const [attempts, setAttempts] = useState<AttemptHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(Boolean(getStoredToken()));
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getStoredToken()));

  useEffect(() => {
    const token = getStoredToken();

    if (!token) return;

    let cancelled = false;

    async function loadHistory() {
      setIsLoading(true);
      setError(null);

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
        const response = await fetch(`${apiUrl}/attempts/history`, {
          headers: getAuthHeaders(),
          credentials: 'include',
        });

        if (response.status === 401) {
          clearStoredToken();
          window.dispatchEvent(new Event('speakege-auth-changed'));
          if (!cancelled) setIsAuthenticated(false);
          return;
        }

        if (!response.ok) {
          throw new Error(`Backend вернул ошибку ${response.status}.`);
        }

        const data = await response.json() as AttemptHistoryItem[];
        if (!cancelled) setAttempts(data);
      } catch (caughtError) {
        console.error(caughtError);
        if (!cancelled) {
          setError(caughtError instanceof Error ? caughtError.message : 'Не удалось загрузить историю.');
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void loadHistory();

    return () => {
      cancelled = true;
    };
  }, []);

  if (!isAuthenticated) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12">
        <div className="rounded-2xl border border-blue-100 bg-white p-8 shadow-sm">
          <h1 className="text-2xl font-bold text-gray-950">История попыток</h1>
          <p className="mt-3 text-gray-600">
            Войдите или зарегистрируйтесь, чтобы сохранять результаты и смотреть историю попыток.
          </p>
          <div className="mt-6 flex gap-3">
            <Link href="/login" className="rounded-lg bg-blue-600 px-5 py-2.5 font-semibold text-white hover:bg-blue-700">
              Войти
            </Link>
            <Link href="/register" className="rounded-lg bg-gray-100 px-5 py-2.5 font-semibold text-gray-800 hover:bg-gray-200">
              Зарегистрироваться
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-950">История попыток</h1>
        <p className="mt-2 text-gray-600">
          Здесь отображаются AI-проверки, связанные с вашим аккаунтом.
        </p>
      </div>

      {isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-gray-500">
          Загружаем историю...
        </div>
      )}

      {error && !isLoading && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-700">
          {error}
        </div>
      )}

      {!isLoading && !error && attempts.length === 0 && (
        <div className="rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
          <h2 className="text-xl font-bold text-gray-950">Попыток пока нет</h2>
          <p className="mt-2 text-gray-600">Пройдите демо-задание, чтобы увидеть результат здесь.</p>
          <Link href="/exam/task2" className="mt-6 inline-flex rounded-lg bg-blue-600 px-5 py-2.5 font-semibold text-white hover:bg-blue-700">
            Попробовать задание
          </Link>
        </div>
      )}

      {!isLoading && !error && attempts.length > 0 && (
        <div className="space-y-4">
          {attempts.map((attempt) => (
            <article key={attempt.id} className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="font-bold text-gray-950">{getTaskTitle(attempt.task_type)}</h2>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-gray-500">
                    <span>{formatDate(attempt.created_at)}</span>
                    <span>·</span>
                    <span>{sourceLabel(attempt.source)}</span>
                    <span>·</span>
                    <span>{attempt.credit_cost} кредитов</span>
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${statusClassName(attempt.status)}`}>
                      {statusLabel(attempt.status)}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-gray-400">ID: {attempt.id}</p>
                </div>

                <div className="flex items-center gap-4 sm:justify-end">
                  <div className="text-right">
                    <p className="text-xs font-medium uppercase tracking-wide text-gray-500">Балл</p>
                    <p className="text-2xl font-bold text-blue-700">
                      {attempt.total_score ?? '—'} / {attempt.max_score ?? '—'}
                    </p>
                  </div>
                  <Link
                    href={`/results/${attempt.id}`}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
                  >
                    Открыть
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
