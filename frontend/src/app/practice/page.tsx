'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { getAuthHeaders, getStoredToken } from '@/config/auth';
import { TASK_CONFIG, TaskType } from '@/config/tasks';

interface QuestionListItem {
  id: string;
  task_type: TaskType;
  title: string;
  is_demo: boolean;
  is_curated: boolean;
  position: number;
  prep_seconds: number;
  record_seconds: number;
}

interface AttemptHistoryItem {
  id: string;
  question_id?: string | null;
  task_type: string;
  status: string;
}

type TaskFilter = 'all' | TaskType;

const TASK_ORDER: TaskType[] = ['task1', 'task2', 'task3', 'task4'];
const FILTERS: { id: TaskFilter; label: string }[] = [
  { id: 'all', label: 'Все' },
  { id: 'task1', label: 'Задание 1' },
  { id: 'task2', label: 'Задание 2' },
  { id: 'task3', label: 'Задание 3' },
  { id: 'task4', label: 'Задание 4' },
];

function formatTiming(question: QuestionListItem) {
  const prep = Math.round(question.prep_seconds / 60 * 10) / 10;
  const record = Math.round(question.record_seconds / 60 * 10) / 10;
  return question.prep_seconds > 0
    ? `${prep} мин подготовка · ${record} мин ответ`
    : `${record} мин ответ`;
}

export default function PracticePage() {
  const [questions, setQuestions] = useState<QuestionListItem[]>([]);
  const [attempts, setAttempts] = useState<AttemptHistoryItem[]>([]);
  const [selectedFilter, setSelectedFilter] = useState<TaskFilter>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isAuthenticated = Boolean(getStoredToken());

  useEffect(() => {
    let cancelled = false;

    async function loadPracticeData() {
      setIsLoading(true);
      setError(null);

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
        const questionsResponse = await fetch(`${apiUrl}/questions`, {
          credentials: 'include',
        });

        if (!questionsResponse.ok) {
          throw new Error(`Backend вернул ошибку ${questionsResponse.status}.`);
        }

        const questionsData = await questionsResponse.json() as QuestionListItem[];
        if (!cancelled) setQuestions(questionsData);

        if (getStoredToken()) {
          const attemptsResponse = await fetch(`${apiUrl}/attempts/history`, {
            headers: getAuthHeaders(),
            credentials: 'include',
          });

          if (attemptsResponse.ok) {
            const attemptsData = await attemptsResponse.json() as AttemptHistoryItem[];
            if (!cancelled) setAttempts(attemptsData);
          }
        }
      } catch (caughtError) {
        console.error(caughtError);
        if (!cancelled) {
          setError(caughtError instanceof Error ? caughtError.message : 'Не удалось загрузить задания.');
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void loadPracticeData();

    return () => {
      cancelled = true;
    };
  }, []);

  const attemptedQuestionIds = useMemo(() => {
    return new Set(
      attempts
        .filter((attempt) => attempt.status === 'completed' && attempt.question_id)
        .map((attempt) => attempt.question_id as string),
    );
  }, [attempts]);

  const visibleTaskTypes = selectedFilter === 'all' ? TASK_ORDER : [selectedFilter];

  const questionsByTask = useMemo(() => {
    return TASK_ORDER.reduce<Record<TaskType, QuestionListItem[]>>((acc, taskType) => {
      acc[taskType] = questions
        .filter((question) => question.task_type === taskType)
        .sort((a, b) => a.position - b.position);
      return acc;
    }, {
      task1: [],
      task2: [],
      task3: [],
      task4: [],
    });
  }, [questions]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-950">Практика</h1>
          <p className="mt-2 max-w-2xl text-gray-600">
            Выберите вариант задания. Демо-варианты доступны всем, остальные варианты открыты после входа в аккаунт.
          </p>
        </div>
        {!isAuthenticated && (
          <Link href="/register" className="rounded-lg bg-blue-600 px-5 py-2.5 text-center font-semibold text-white hover:bg-blue-700">
            Зарегистрироваться
          </Link>
        )}
      </div>

      <div className="mb-6 flex flex-wrap gap-2">
        {FILTERS.map((filter) => (
          <button
            key={filter.id}
            type="button"
            onClick={() => setSelectedFilter(filter.id)}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
              selectedFilter === filter.id
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 ring-1 ring-gray-200 hover:bg-gray-50'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-gray-500">
          Загружаем задания...
        </div>
      )}

      {error && !isLoading && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-700">
          {error}
        </div>
      )}

      {!isLoading && !error && (
        <div className="space-y-8">
          {visibleTaskTypes.map((taskType) => (
            <section key={taskType} className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-950">{TASK_CONFIG[taskType].title}</h2>
                  <p className="text-sm text-gray-500">{TASK_CONFIG[taskType].description}</p>
                </div>
                <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-semibold text-gray-700">
                  {questionsByTask[taskType].length} вариантов
                </span>
              </div>

              {questionsByTask[taskType].length === 0 ? (
                <p className="rounded-lg bg-gray-50 p-4 text-sm text-gray-500">Варианты пока не загружены.</p>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {questionsByTask[taskType].map((question) => {
                    const isLocked = !question.is_demo && !isAuthenticated;
                    const isAttempted = attemptedQuestionIds.has(question.id);
                    const href = isLocked
                      ? '/register'
                      : `/exam/${question.task_type}?questionId=${encodeURIComponent(question.id)}`;

                    return (
                      <Link
                        key={question.id}
                        href={href}
                        className={`rounded-xl border p-4 transition ${
                          isLocked
                            ? 'border-gray-200 bg-gray-50 hover:bg-gray-100'
                            : 'border-blue-100 bg-blue-50/40 hover:border-blue-300 hover:bg-blue-50'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h3 className="font-bold text-gray-950">Вариант {question.position}</h3>
                            <p className="mt-1 text-sm text-gray-600">{question.title}</p>
                          </div>
                          <span className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${
                            question.is_demo
                              ? 'bg-green-100 text-green-700'
                              : isLocked
                                ? 'bg-gray-200 text-gray-600'
                                : 'bg-blue-100 text-blue-700'
                          }`}>
                            {question.is_demo ? 'Демо' : isLocked ? 'После входа' : 'Доступно'}
                          </span>
                        </div>
                        <p className="mt-3 text-xs text-gray-500">{formatTiming(question)}</p>
                        <div className="mt-4 flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold text-blue-700">
                            {isLocked ? 'Зарегистрироваться →' : 'Начать →'}
                          </p>
                          {isAuthenticated && isAttempted && (
                            <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                              Пройдено
                            </span>
                          )}
                        </div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
