'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { AuthUser, clearStoredToken, getAuthHeaders, getStoredToken } from '@/config/auth';

export default function SiteHeader() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadUser() {
      const token = getStoredToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';
        const response = await fetch(`${apiUrl}/auth/user`, {
          headers: getAuthHeaders(),
          credentials: 'include',
        });

        if (!response.ok) {
          clearStoredToken();
          if (!cancelled) setUser(null);
          return;
        }

        const data = await response.json() as AuthUser;
        if (!cancelled) setUser(data);
      } catch (caughtError) {
        console.warn('Could not load auth user', caughtError);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void loadUser();

    function handleAuthChanged() {
      setIsLoading(true);
      void loadUser();
    }

    window.addEventListener('speakege-auth-changed', handleAuthChanged);

    return () => {
      cancelled = true;
      window.removeEventListener('speakege-auth-changed', handleAuthChanged);
    };
  }, []);

  function handleLogout() {
    clearStoredToken();
    setUser(null);
    window.dispatchEvent(new Event('speakege-auth-changed'));
  }

  return (
    <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2 font-bold text-gray-950">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-sm font-black text-white">
            SE
          </span>
          <span className="hidden sm:inline">SpeakEGE</span>
        </Link>

        <nav className="flex items-center gap-2" aria-label="Навигация пользователя">
          {user ? (
            <>
              <Link
                href="/account"
                className="rounded-lg px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-100 hover:text-gray-950"
              >
                Кабинет
              </Link>
              <Link
                href="/history"
                className="hidden rounded-lg px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-100 hover:text-gray-950 sm:inline"
              >
                История
              </Link>
              <span className="hidden rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700 md:inline">
                {user.credit_balance} кредитов
              </span>
              <span className="hidden max-w-[220px] truncate text-sm font-medium text-gray-700 sm:inline">
                {user.email}
              </span>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-lg px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-100 hover:text-gray-950"
              >
                Выйти
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="rounded-lg px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-100 hover:text-gray-950"
              >
                Войти
              </Link>
              <Link
                href="/register"
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
              >
                Зарегистрироваться
              </Link>
            </>
          )}
          {isLoading && <span className="sr-only">Проверяем авторизацию...</span>}
        </nav>
      </div>
    </header>
  );
}
