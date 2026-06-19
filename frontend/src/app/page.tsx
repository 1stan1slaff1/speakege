import Link from 'next/link';
import { TASK_CONFIG, TaskType } from '@/config/tasks';

const TASK_ORDER: TaskType[] = ['task1', 'task2', 'task3', 'task4'];

const TASK_SUMMARIES: Record<TaskType, string> = {
  task1: 'Одно демо-задание на чтение текста вслух с официальным таймером.',
  task2: 'Одно демо-задание на 4 прямых вопроса по рекламному объявлению.',
  task3: 'Одно демо-интервью: вопросы проигрываются голосом по одному.',
  task4: 'Одно демо-задание с голосовым сообщением другу по двум иллюстрациям.',
};

const FUTURE_BENEFITS = [
  'больше вариантов по каждому типу задания',
  'история попыток и прогресс по критериям',
  'дополнительные задания пакетами после бесплатного лимита',
];

export default function Home() {
  return (
    <div className="bg-gray-50">
      <section className="mx-auto max-w-6xl px-4 py-14 sm:px-6 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <p className="mb-4 inline-flex rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 ring-1 ring-blue-100">
              Демо-доступ без регистрации
            </p>
            <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-gray-950 sm:text-5xl">
              Тренажёр устной части ЕГЭ по английскому с AI-разбором
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-gray-600">
              Сейчас доступно по одному фиксированному демо-заданию каждого типа. Пройдите задание в формате экзамена, запишите ответ или загрузите аудио и получите разбор по критериям.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/exam/task2"
                className="rounded-lg bg-blue-600 px-6 py-3 text-center font-semibold text-white transition-colors hover:bg-blue-700"
              >
                Попробовать демо
              </Link>
              <Link
                href="/register"
                className="rounded-lg bg-white px-6 py-3 text-center font-semibold text-gray-800 ring-1 ring-gray-200 transition-colors hover:bg-gray-50"
              >
                Узнать про регистрацию
              </Link>
            </div>
          </div>

          <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-bold text-gray-950">Что будет после регистрации</h2>
            <p className="mt-2 text-sm leading-6 text-gray-600">
              Регистрация пока в разработке. План: дать новым пользователям бесплатный набор заданий, сохранить историю и открыть доступ к дополнительным вариантам.
            </p>
            <ul className="mt-5 space-y-3">
              {FUTURE_BENEFITS.map((benefit) => (
                <li key={benefit} className="flex gap-3 text-sm text-gray-700">
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-green-100 text-xs font-bold text-green-700">
                    ✓
                  </span>
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-16 sm:px-6">
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-950">Демо-задания</h2>
            <p className="mt-2 text-gray-600">По одному фиксированному заданию на каждый тип устной части.</p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {TASK_ORDER.map((taskType) => {
            const task = TASK_CONFIG[taskType];
            return (
              <Link
                key={taskType}
                href={`/exam/${taskType}`}
                className="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md"
              >
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 font-bold text-blue-700">
                  {taskType.replace('task', '')}
                </div>
                <h3 className="font-bold text-gray-950 group-hover:text-blue-700">{task.title}</h3>
                <p className="mt-3 text-sm leading-6 text-gray-600">{TASK_SUMMARIES[taskType]}</p>
                <p className="mt-4 text-sm font-semibold text-blue-600">Начать →</p>
              </Link>
            );
          })}
        </div>
      </section>
    </div>
  );
}
