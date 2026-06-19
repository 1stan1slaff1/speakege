import Link from 'next/link';

export default function LoginPage() {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-70px)] max-w-md items-center px-4 py-12">
      <div className="w-full rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <p className="mb-3 inline-flex rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700 ring-1 ring-amber-100">
          Скоро
        </p>
        <h1 className="text-2xl font-bold text-gray-950">Вход в аккаунт</h1>
        <p className="mt-3 text-sm leading-6 text-gray-600">
          Авторизация ещё не подключена. Сейчас можно проходить фиксированные демо-задания без аккаунта, а позже здесь появится вход для сохранения истории и доступа к дополнительным заданиям.
        </p>

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
            Войти
          </button>
        </div>

        <div className="mt-6 flex items-center justify-between text-sm">
          <Link href="/" className="font-medium text-gray-600 hover:text-gray-950">
            На главную
          </Link>
          <Link href="/register" className="font-semibold text-blue-600 hover:text-blue-700">
            Зарегистрироваться
          </Link>
        </div>
      </div>
    </div>
  );
}
