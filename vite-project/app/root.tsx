import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from 'react-router';

import type { Route } from './+types/root';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastContainer } from './components/ErrorToast';
import { useErrorHandler } from './hooks/useErrorHandler';
import './app.css';

export const links: Route.LinksFunction = () => [
  { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
  {
    rel: 'preconnect',
    href: 'https://fonts.gstatic.com',
    crossOrigin: 'anonymous',
  },
  {
    rel: 'stylesheet',
    href: 'https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap',
  },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <head>
        <meta charSet="utf-8" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, viewport-fit=cover"
        />
        <meta
          name="description"
          content="AWS CloudOps Engineer - Associate 認定試験対策アプリ。実践的な問題で効率的に学習できます。"
        />
        <meta
          name="keywords"
          content="AWS, CloudOps, 試験対策, 認定試験, Associate, 学習アプリ"
        />
        <meta name="author" content="AWS CloudOps 試験対策アプリ" />
        <meta name="theme-color" content="#3b82f6" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta
          name="apple-mobile-web-app-title"
          content="AWS CloudOps 試験対策"
        />
        <meta name="format-detection" content="telephone=no" />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  const { toasts, removeToast } = useErrorHandler();

  return (
    <ErrorBoundary>
      <Outlet />
      <ToastContainer toasts={toasts} onRemoveToast={removeToast} />
    </ErrorBoundary>
  );
}

export function RootErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message = '申し訳ございません';
  let details = '予期しないエラーが発生しました。';
  let stack: string | undefined;

  if (isRouteErrorResponse(error)) {
    message =
      error.status === 404 ? 'ページが見つかりません' : 'エラーが発生しました';
    details =
      error.status === 404
        ? 'お探しのページは見つかりませんでした。'
        : error.statusText || details;
  } else if (import.meta.env.DEV && error && error instanceof Error) {
    details = error.message;
    stack = error.stack;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 text-center">
        <div className="flex items-center justify-center w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full mx-auto mb-4">
          <svg
            className="w-8 h-8 text-red-600 dark:text-red-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        </div>

        <h1 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          {message}
        </h1>

        <p className="text-gray-600 dark:text-gray-300 mb-6">{details}</p>

        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={() => (window.location.href = '/')}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            ホームに戻る
          </button>

          <button
            onClick={() => window.location.reload()}
            className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors font-medium"
          >
            ページを再読み込み
          </button>
        </div>

        {/* 開発環境でのエラー詳細表示 */}
        {import.meta.env.DEV && stack && (
          <details className="mt-6 text-left">
            <summary className="cursor-pointer text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">
              エラー詳細を表示
            </summary>
            <pre className="mt-2 p-3 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono text-gray-800 dark:text-gray-200 overflow-auto max-h-40 whitespace-pre-wrap">
              {stack}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}
