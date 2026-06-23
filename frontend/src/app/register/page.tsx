'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';
import { DEFAULT_FREE_REGISTERED_CREDITS } from '@/config/billing';
import { storeToken, TokenResponse } from '@/config/auth';

const PLANNED_FREE_LIMITS = [
  `${DEFAULT_FREE_REGISTERED_CREDITS} стартовых кредитов после регистрации`,
  'гибкая стоимость проверки в зависимости от типа задания',
  'история результатов и разбор прогресса',
  'покупка дополнительных кредитов для AI-проверок',
];

async function readApiError(response: Response) {
  const body = await response.text();
  if (!body) return `Backend вернул ошибку ${response.status}.`;

  try {
    const parsed = JSON.parse(body) as { detail?: unknown };
    if (typeof parsed.detail === 'string') return parsed.detail;
    if (parsed.detail) return JSON.stringify(parsed.detail);
  } catch {
    // ignore non-json response
  }

  return body;
}

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
      const response = await fetch(`${apiUrl}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error(await readApiError(response));
      }

      const data = await response.json() as TokenResponse;
      storeToken(data.access_token);
      window.dispatchEvent(new Event('speakege-auth-changed'));
      router.push('/');
    } catch (caughtError) {
      console.error(caughtError);
      setError(caughtError instanceof Error ? caughtError.message : 'Не удалось зарегистрироваться.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto grid min-h-[calc(100vh-70px)] max-w-5xl gap-8 px-4 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
      <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
        <p className="mb-3 inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 ring-1 ring-blue-100">
          Аккаунты MVP
        </p>
        <h1 className="text-3xl font-bold text-gray-950">Создайте аккаунт, чтобы открыть больше заданий</h1>
        <p className="mt-4 text-sm leading-6 text-gray-600">
          Сейчас доступны фиксированные демо-задания без регистрации. Аккаунт позволит связать ваши гостевые попытки с пользователем и подготовит доступ к кредитам, истории и дополнительным заданиям.
        </p>
        <ul className="mt-6 space-y-3">
          {PLANNED_FREE_LIMITS.map((item) => (
            <li key={item} className="flex gap-3 text-sm text-gray-700">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                ✓
              </span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-gray-950">Форма регистрации</h2>
        <p className="mt-2 text-sm text-gray-500">Минимальная регистрация уже подключена. Кредиты будут подключены следующим этапом.</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Email
            <input
              required
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label className="block text-sm font-medium text-gray-700">
            Пароль
            <input
              required
              minLength={8}
              maxLength={128}
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="минимум 8 символов"
              className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </label>

          {error && (
            <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
          >
            {isSubmitting ? 'Регистрируем...' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="mt-6 flex items-center justify-between text-sm">
          <Link href="/" className="font-medium text-gray-600 hover:text-gray-950">
            На главную
          </Link>
          <Link href="/login" className="font-semibold text-blue-600 hover:text-blue-700">
            Уже есть аккаунт? Войти
          </Link>
        </div>
      </div>
    </div>
  );
}
