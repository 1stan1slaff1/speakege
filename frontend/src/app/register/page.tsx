import Link from 'next/link';

const PLANNED_FREE_LIMITS = [
  '5 бесплатных заданий каждого типа после регистрации',
  'несколько попыток на задание для повторной тренировки',
  'история результатов и разбор прогресса',
  'покупка дополнительных заданий пакетами',
];

export default function RegisterPage() {
  return (
    <div className="mx-auto grid min-h-[calc(100vh-70px)] max-w-5xl gap-8 px-4 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
      <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
        <p className="mb-3 inline-flex rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700 ring-1 ring-amber-100">
          Регистрация в разработке
        </p>
        <h1 className="text-3xl font-bold text-gray-950">Создайте аккаунт, чтобы открыть больше заданий</h1>
        <p className="mt-4 text-sm leading-6 text-gray-600">
          Сейчас доступны фиксированные демо-задания без регистрации. В следующем этапе аккаунт позволит получать больше вариантов, сохранять историю и покупать дополнительные задания пакетами.
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
        <p className="mt-2 text-sm text-gray-500">Пока неактивна — backend auth ещё не подключён.</p>

        <div className="mt-6 space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Email
            <input
              disabled
              type="email"
              placeholder="you@example.com"
              className="mt-1 w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-gray-500"
            />
          </label>
          <label className="block text-sm font-medium text-gray-700">
            Пароль
            <input
              disabled
              type="password"
              placeholder="••••••••"
              className="mt-1 w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-gray-500"
            />
          </label>
          <button
            disabled
            className="w-full cursor-not-allowed rounded-lg bg-gray-300 px-4 py-2.5 font-semibold text-gray-500"
          >
            Зарегистрироваться
          </button>
        </div>

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
