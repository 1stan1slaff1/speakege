'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { LEARN_TOPICS } from '@/config/learn';

function getSlug(param: string | string[] | undefined) {
  if (Array.isArray(param)) return param[0];
  return param;
}

export default function LearnTopicPage() {
  const params = useParams();
  const slug = getSlug(params.slug);
  const topic = slug ? LEARN_TOPICS[slug] : undefined;

  if (!topic) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12">
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
          <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">Материал не найден</p>
          <h1 className="text-3xl font-bold text-gray-950">Такой темы пока нет</h1>
          <p className="mt-4 leading-7 text-gray-600">
            Возможно, ссылка устарела или материал ещё не добавлен. Вернитесь к списку тем или продолжите тренировку.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/learn" className="rounded-lg bg-blue-600 px-5 py-2.5 font-semibold text-white hover:bg-blue-700">
              Все материалы
            </Link>
            <Link href="/practice" className="rounded-lg bg-gray-100 px-5 py-2.5 font-semibold text-gray-800 hover:bg-gray-200">
              К практике
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <div className="mb-6">
        <Link href="/learn" className="text-sm font-semibold text-blue-600 hover:text-blue-700">
          ← Все материалы
        </Link>
      </div>

      <article className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="mb-5 flex flex-wrap gap-2">
          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 ring-1 ring-blue-100">
            {topic.category}
          </span>
          {topic.taskLabels.map((label) => (
            <span key={label} className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-700">
              {label}
            </span>
          ))}
        </div>

        <h1 className="text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">{topic.title}</h1>
        <p className="mt-5 text-lg leading-8 text-gray-700">{topic.lead}</p>

        <section className="mt-8">
          <h2 className="text-xl font-bold text-gray-950">Главное</h2>
          <ul className="mt-4 space-y-3">
            {topic.keyPoints.map((point) => (
              <li key={point} className="flex gap-3 text-gray-700">
                <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                  ✓
                </span>
                <span className="leading-7">{point}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-green-100 bg-green-50 p-5">
            <h2 className="font-bold text-green-950">Хорошие формулировки</h2>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-green-900">
              {topic.goodExamples.map((example) => (
                <li key={example}>• {example}</li>
              ))}
            </ul>
          </div>

          {topic.badExamples && topic.badExamples.length > 0 && (
            <div className="rounded-xl border border-red-100 bg-red-50 p-5">
              <h2 className="font-bold text-red-950">Чего избегать</h2>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-red-900">
                {topic.badExamples.map((example) => (
                  <li key={example}>• {example}</li>
                ))}
              </ul>
            </div>
          )}
        </section>

        <section className="mt-8 rounded-xl border border-amber-100 bg-amber-50 p-5">
          <h2 className="font-bold text-amber-950">Экзаменационный совет</h2>
          <p className="mt-2 leading-7 text-amber-900">{topic.examTip}</p>
        </section>

        <section className="mt-8 rounded-xl border border-gray-200 bg-gray-50 p-5">
          <h2 className="font-bold text-gray-950">Мини-тренировка</h2>
          <p className="mt-2 leading-7 text-gray-700">{topic.practicePrompt}</p>
        </section>
      </article>

      <div className="mt-8 flex flex-wrap gap-3">
        <Link href="/practice" className="rounded-lg bg-blue-600 px-5 py-2.5 font-semibold text-white hover:bg-blue-700">
          Перейти к практике
        </Link>
        <Link href="/history" className="rounded-lg bg-white px-5 py-2.5 font-semibold text-blue-700 ring-1 ring-blue-200 hover:bg-blue-50">
          История попыток
        </Link>
      </div>
    </div>
  );
}
