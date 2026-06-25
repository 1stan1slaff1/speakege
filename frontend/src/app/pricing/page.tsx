import Link from 'next/link';
import { DEFAULT_CURRENCY_LABEL, DEFAULT_TASK_CREDIT_COST } from '@/config/billing';
import { TASK_CONFIG, TaskType } from '@/config/tasks';

const TASK_ORDER: TaskType[] = ['task1', 'task2', 'task3', 'task4'];

const PACKAGES = [
  {
    name: 'Старт',
    credits: 40,
    price: 149,
    description: 'Для короткой тренировки и проверки нескольких ответов.',
  },
  {
    name: 'Практика',
    credits: 100,
    price: 299,
    description: 'Оптимальный пакет для регулярной подготовки.',
    highlighted: true,
  },
  {
    name: 'Интенсив',
    credits: 250,
    price: 699,
    description: 'Для активной подготовки перед экзаменом.',
  },
];

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <section className="mb-10 max-w-3xl">
        <p className="mb-4 inline-flex rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 ring-1 ring-blue-100">
          Оплата скоро
        </p>
        <h1 className="text-4xl font-bold tracking-tight text-gray-950">
          Пакеты кредитов для AI-проверок
        </h1>
        <p className="mt-4 text-lg leading-8 text-gray-600">
          Кредиты списываются за AI-разбор ответа. Сейчас покупка ещё не подключена — эта страница показывает будущую модель оплаты и поможет протестировать UX до интеграции YooKassa/Robokassa.
        </p>
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        {PACKAGES.map((pack) => (
          <article
            key={pack.name}
            className={`relative rounded-2xl border bg-white p-6 shadow-sm ${
              pack.highlighted ? 'border-blue-300 ring-2 ring-blue-100' : 'border-gray-200'
            }`}
          >
            {pack.highlighted && (
              <span className="absolute right-4 top-4 rounded-full bg-blue-600 px-3 py-1 text-xs font-bold text-white">
                Популярный
              </span>
            )}
            <h2 className="text-xl font-bold text-gray-950">{pack.name}</h2>
            <p className="mt-3 text-sm leading-6 text-gray-600">{pack.description}</p>
            <div className="mt-6">
              <p className="text-4xl font-bold text-gray-950">{pack.credits}</p>
              <p className="text-sm font-medium text-gray-500">{DEFAULT_CURRENCY_LABEL}</p>
            </div>
            <p className="mt-5 text-2xl font-bold text-blue-700">{pack.price} ₽</p>
            <button
              type="button"
              disabled
              className="mt-6 w-full cursor-not-allowed rounded-lg bg-gray-300 px-4 py-2.5 font-semibold text-gray-500"
            >
              Оплата скоро
            </button>
          </article>
        ))}
      </section>

      <section className="mt-10 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-gray-950">Стоимость проверки</h2>
          <p className="mt-2 text-sm leading-6 text-gray-600">
            Стоимость зависит от типа задания. Её можно оперативно изменить в backend config.
          </p>
          <div className="mt-5 space-y-3">
            {TASK_ORDER.map((taskType) => (
              <div key={taskType} className="flex items-center justify-between gap-4 rounded-lg bg-gray-50 px-4 py-3">
                <span className="text-sm font-medium text-gray-800">{TASK_CONFIG[taskType].title}</span>
                <span className="shrink-0 text-sm font-bold text-blue-700">
                  {DEFAULT_TASK_CREDIT_COST[taskType]} {DEFAULT_CURRENCY_LABEL}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-blue-100 bg-blue-50 p-6">
          <h2 className="text-xl font-bold text-blue-950">Что будет дальше</h2>
          <ul className="mt-4 space-y-3 text-sm leading-6 text-blue-900">
            <li>• Подключим платежи через YooKassa или Robokassa.</li>
            <li>• После успешного платежа webhook будет добавлять кредиты в credit_ledger.</li>
            <li>• В личном кабинете появится история покупок и пополнений.</li>
            <li>• До платежей тестовые кредиты можно выдавать вручную dev-скриптом.</li>
          </ul>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Link
              href="/account"
              className="rounded-lg bg-blue-600 px-5 py-2.5 text-center font-semibold text-white hover:bg-blue-700"
            >
              В кабинет
            </Link>
            <Link
              href="/exam/task2"
              className="rounded-lg bg-white px-5 py-2.5 text-center font-semibold text-blue-700 ring-1 ring-blue-200 hover:bg-blue-50"
            >
              Продолжить тренировку
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
