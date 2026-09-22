import Link from 'next/link';
import { LEARN_TOPIC_LIST } from '@/config/learn';

const CATEGORY_ORDER = ['Содержание', 'Организация', 'Язык', 'Произношение'];

export default function LearnPage() {
  const groupedTopics = CATEGORY_ORDER.map((category) => ({
    category,
    topics: LEARN_TOPIC_LIST.filter((topic) => topic.category === category),
  })).filter((group) => group.topics.length > 0);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <section className="mb-10 max-w-3xl">
        <p className="mb-4 inline-flex rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 ring-1 ring-blue-100">
          Материалы для повторения
        </p>
        <h1 className="text-4xl font-bold tracking-tight text-gray-950">Что повторить после AI-разбора</h1>
        <p className="mt-4 text-lg leading-8 text-gray-600">
          Короткие материалы по темам, которые появляются в блоке «Что повторить» на странице результата.
        </p>
      </section>

      <div className="space-y-8">
        {groupedTopics.map((group) => (
          <section key={group.category} className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-950">{group.category}</h2>
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              {group.topics.map((topic) => (
                <Link
                  key={topic.slug}
                  href={`/learn/${topic.slug}`}
                  className="rounded-xl border border-gray-200 bg-gray-50 p-4 transition hover:border-blue-200 hover:bg-blue-50"
                >
                  <div className="flex flex-wrap gap-2">
                    {topic.taskLabels.map((label) => (
                      <span key={label} className="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-gray-600 ring-1 ring-gray-200">
                        {label}
                      </span>
                    ))}
                  </div>
                  <h3 className="mt-3 font-bold text-gray-950">{topic.title}</h3>
                  <p className="mt-2 line-clamp-3 text-sm leading-6 text-gray-600">{topic.lead}</p>
                  <p className="mt-3 text-sm font-semibold text-blue-600">Открыть материал →</p>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
