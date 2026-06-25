'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { AuthUser, clearStoredToken, getAuthHeaders, getStoredToken } from '@/config/auth';
import { BillingPublicInfo, DEFAULT_CURRENCY_LABEL, DEFAULT_TASK_CREDIT_COST } from '@/config/billing';
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

const TASK_ORDER: TaskType[] = ['task1', 'task2', 'task3', 'task4'];

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
  if (source === 'uploaded') return 'Файл';
  if (source === 'recorded') return 'Запись';
  return source;
}

export default function AccountPage() {
  const hasToken = Boolean(getStoredToken());
  const [user, setUser] = useState<AuthUser | null>(null);
  const [attempts, setAttempts] = useState<AttemptHistoryItem[]>([]);
  const [billingInfo, setBillingInfo] = useState<BillingPublicInfo | null>(null);
  const [isLoading, setIsLoading] = useState(hasToken);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;

    let cancelled = false;

    async function loadAccountData() {
      setIsLoading(true);
      setError(null);

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
        const [userResponse, attemptsResponse, billingResponse] = await Promise.all([
          fetch(`${apiUrl}/auth/user`, {
            headers: getAuthHeaders(),
            credentials: 'include',
          }),
          fetch(`${apiUrl}/attempts/history`, {
            headers: getAuthHeaders(),
            credentials: 'include',
          }),
          fetch(`${apiUrl}/billing/public`, {
            credentials: 'include',
          }),
        ]);

        if (userResponse.status === 401) {
          clearStoredToken();
          window.dispatchEvent(new Event('speakege-auth-changed'));
          if (!cancelled) setUser(null);
          return;
        }

        if (!userResponse.ok) throw new Error(`Не удалось загрузить профиль: ${userResponse.status}`);
        if (!attemptsResponse.ok) throw new Error(`Не удалось загрузить историю: ${attemptsResponse.status}`);

        const userData = await userResponse.json() as AuthUser;
        const attemptsData = await attemptsResponse.json() as AttemptHistoryItem[];
        const billingData = billingResponse.ok
          ? await billingResponse.json() as BillingPublicInfo
          : null;

        if (cancelled) return;

        setUser(userData);
        setAttempts(attemptsData);
        setBillingInfo(billingData);
      } catch (caughtError) {
        console.error(caughtError);
        if (!cancelled) {
          setError(caughtError instanceof Error ? caughtError.message : 'Не удалось загрузить кабинет.');
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void loadAccountData();

    return () => {
      cancelled = true;
    };
  }, []);

  if (!hasToken) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12">
        <div className="rounded-2xl border border-blue-100 bg-white p-8 shadow-sm">
          <h1 className="text-2xl font-bold text-gray-950">Личный кабинет</h1>
          <p className="mt-3 text-gray-600">
            Войдите или зарегистрируйтесь, чтобы видеть баланс кредитов, историю попыток и будущие покупки.
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

  const recentAttempts = attempts.slice(0, 5);
  const completedAttempts = attempts.filter((attempt) => attempt.status === 'completed');
  const averageScore = completedAttempts.length
    ? completedAttempts.reduce((sum, attempt) => sum + (attempt.total_score ?? 0), 0) / completedAttempts.length
    : null;
  const taskCreditCost = billingInfo?.task_credit_cost ?? DEFAULT_TASK_CREDIT_COST;
  const currencyLabel = billingInfo?.currency_label ?? DEFAULT_CURRENCY_LABEL;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-950">Личный кабинет</h1>
          <p className="mt-2 text-gray-600">Баланс, стоимость проверок и последние попытки.</p>
        </div>
        <Link href="/history" className="rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-blue-700 ring-1 ring-blue-200 hover:bg-blue-50">
          Вся история
        </Link>
      </div>

      {isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-gray-500">
          Загружаем кабинет...
        </div>
      )}

      {error && !isLoading && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-700">
          {error}
        </div>
      )}

      {!isLoading && !error && user && (
        <>
          <section className="grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-blue-100 bg-blue-50 p-6">
              <p className="text-sm font-semibold text-blue-700">Баланс</p>
              <p className="mt-2 text-4xl font-bold text-blue-950">{user.credit_balance}</p>
              <p className="mt-1 text-sm text-blue-700">{currencyLabel}</p>
            </div>
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <p className="text-sm font-semibold text-gray-500">Аккаунт</p>
              <p className="mt-2 truncate text-lg font-bold text-gray-950">{user.email}</p>
              <p className="mt-1 text-sm text-gray-500">Создан: {formatDate(user.created_at)}</p>
            </div>
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <p className="text-sm font-semibold text-gray-500">Статистика</p>
              <p className="mt-2 text-lg font-bold text-gray-950">{completedAttempts.length} завершённых попыток</p>
              <p className="mt-1 text-sm text-gray-500">
                Средний балл: {averageScore === null ? '—' : averageScore.toFixed(1)}
              </p>
            </div>
          </section>

          <section className="mt-8 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold text-gray-950">Стоимость AI-проверок</h2>
              <p className="mt-2 text-sm text-gray-600">Стоимость можно менять в backend config.</p>
              <div className="mt-5 space-y-3">
                {TASK_ORDER.map((taskType) => (
                  <div key={taskType} className="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-3">
                    <span className="text-sm font-medium text-gray-800">{TASK_CONFIG[taskType].title}</span>
                    <span className="text-sm font-bold text-blue-700">{taskCreditCost[taskType]} {currencyLabel}</span>
                  </div>
                ))}
              </div>
              <Link
                href="/pricing"
                className="mt-6 block w-full rounded-lg bg-blue-600 px-4 py-2.5 text-center font-semibold text-white hover:bg-blue-700"
              >
                Купить кредиты
              </Link>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between gap-4">
                <h2 className="text-xl font-bold text-gray-950">Последние попытки</h2>
                <Link href="/history" className="text-sm font-semibold text-blue-600 hover:text-blue-700">
                  Все →
                </Link>
              </div>

              {recentAttempts.length === 0 ? (
                <div className="mt-6 rounded-lg bg-gray-50 p-6 text-center">
                  <p className="font-medium text-gray-800">Попыток пока нет</p>
                  <p className="mt-1 text-sm text-gray-500">Пройдите демо-задание, чтобы увидеть результат здесь.</p>
                  <Link href="/exam/task2" className="mt-4 inline-flex rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
                    Попробовать задание
                  </Link>
                </div>
              ) : (
                <div className="mt-5 divide-y divide-gray-100">
                  {recentAttempts.map((attempt) => (
                    <div key={attempt.id} className="flex items-center justify-between gap-4 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{getTaskTitle(attempt.task_type)}</p>
                        <p className="mt-1 text-xs text-gray-500">
                          {formatDate(attempt.created_at)} · {sourceLabel(attempt.source)}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-bold text-blue-700">
                          {attempt.total_score ?? '—'} / {attempt.max_score ?? '—'}
                        </span>
                        <Link href={`/results/${attempt.id}`} className="rounded-lg bg-gray-100 px-3 py-1.5 text-sm font-semibold text-gray-800 hover:bg-gray-200">
                          Открыть
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
