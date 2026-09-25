'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { DEFAULT_FREE_REGISTERED_CREDITS, DEFAULT_TASK_CREDIT_COST } from '@/config/billing';
import { getStoredToken } from '@/config/auth';
import { TASK_CONFIG, TaskType } from '@/config/tasks';

const TASK_ORDER: TaskType[] = ['task1', 'task2', 'task3', 'task4'];

const TASK_SUMMARIES: Record<TaskType, string> = {
  task1: 'Чтение текста вслух с таймером: 90 секунд на подготовку и 90 секунд на ответ.',
  task2: 'Четыре прямых вопроса по рекламному объявлению, по 20 секунд на каждый вопрос.',
  task3: 'Условное интервью: пять вопросов интервьюера, по 40 секунд на каждый ответ.',
  task4: 'Голосовое сообщение другу по двум иллюстрациям для школьного проекта.',
};

const ACCOUNT_BENEFITS = [
  `${DEFAULT_FREE_REGISTERED_CREDITS} стартовых кредитов для AI-проверок`,
  'больше вариантов по каждому типу задания',
  'история попыток и результаты в личном кабинете',
];

const PREPARATION_STEPS = [
  'Выберите вариант в разделе практики.',
  'Запишите ответ в формате экзамена.',
  'Откройте результат и повторите слабые темы.',
];

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    function syncAuthState() {
      setIsAuthenticated(Boolean(getStoredToken()));
    }

    syncAuthState();
    window.addEventListener('speakege-auth-changed', syncAuthState);

    return () => {
      window.removeEventListener('speakege-auth-changed', syncAuthState);
    };
  }, []);

  const isLoggedIn = isAuthenticated === true;

  return (
    <div className="bg-gray-50">
      <section className="mx-auto max-w-6xl px-4 py-14 sm:px-6 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <p className="mb-4 inline-flex rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 ring-1 ring-blue-100">
              Тренировка в формате устной части ЕГЭ
            </p>
            <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-gray-950 sm:text-5xl">
              Тренажёр устной части ЕГЭ по английскому с AI-разбором
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-gray-600">
              Выберите вариант задания, пройдите его с экзаменационным таймером, запишите ответ или загрузите аудио и получите разбор по критериям.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/practice"
                className="rounded-lg bg-blue-600 px-6 py-3 text-center font-semibold text-white transition-colors hover:bg-blue-700"
              >
                Выбрать задание
              </Link>
              {isAuthenticated === false ? (
                <Link
                  href="/register"
                  className="rounded-lg bg-white px-6 py-3 text-center font-semibold text-gray-800 ring-1 ring-gray-200 transition-colors hover:bg-gray-50"
                >
                  Создать аккаунт
                </Link>
              ) : (
                <Link
                  href="/learn"
                  className="rounded-lg bg-white px-6 py-3 text-center font-semibold text-gray-800 ring-1 ring-gray-200 transition-colors hover:bg-gray-50"
                >
                  Материалы
                </Link>
              )}
            </div>
          </div>

          {isLoggedIn || isAuthenticated === null ? (
            <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-bold text-gray-950">Как продолжить</h2>
              <p className="mt-2 text-sm leading-6 text-gray-600">
                Тренировка строится вокруг короткого цикла: задание, запись ответа, AI-разбор и повторение слабых тем.
              </p>
              <ol className="mt-5 space-y-3">
                {PREPARATION_STEPS.map((step, index) => (
                  <li key={step} className="flex gap-3 text-sm text-gray-700">
                    <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                      {index + 1}
                    </span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          ) : (
            <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-bold text-gray-950">Что даёт аккаунт</h2>
              <p className="mt-2 text-sm leading-6 text-gray-600">
                Аккаунт сохраняет ваши результаты, открывает дополнительные варианты и даёт стартовый баланс для AI-проверок.
              </p>
              <p className="mt-4 rounded-lg bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-800">
                Стартовый баланс: {DEFAULT_FREE_REGISTERED_CREDITS} кредитов
              </p>
              <ul className="mt-5 space-y-3">
                {ACCOUNT_BENEFITS.map((benefit) => (
                  <li key={benefit} className="flex gap-3 text-sm text-gray-700">
                    <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-green-100 text-xs font-bold text-green-700">
                      ✓
                    </span>
                    <span>{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-16 sm:px-6">
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-950">Задания устной части</h2>
            <p className="mt-2 text-gray-600">Откройте раздел практики, чтобы выбрать демо или дополнительный вариант.</p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {TASK_ORDER.map((taskType) => {
            const task = TASK_CONFIG[taskType];
            return (
              <Link
                key={taskType}
                href="/practice"
                className="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md"
              >
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 font-bold text-blue-700">
                  {taskType.replace('task', '')}
                </div>
                <h3 className="font-bold text-gray-950 group-hover:text-blue-700">{task.title}</h3>
                <p className="mt-3 text-sm leading-6 text-gray-600">{TASK_SUMMARIES[taskType]}</p>
                <p className="mt-4 inline-flex rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-700">
                  AI-проверка: {DEFAULT_TASK_CREDIT_COST[taskType]} кредитов
                </p>
                <p className="mt-4 text-sm font-semibold text-blue-600">Выбрать вариант →</p>
              </Link>
            );
          })}
        </div>
      </section>
    </div>
  );
}
