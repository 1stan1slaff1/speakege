'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
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

function ResultsContent() {
  const searchParams = useSearchParams();
  const raw = searchParams.get('data');

  if (!raw) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <p className="text-red-500">Данные не найдены.</p>
      </div>
    );
  }

  const data = parseSubmissionData(raw);

  if (!data) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <p className="text-red-500">Не удалось прочитать данные результата.</p>
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
