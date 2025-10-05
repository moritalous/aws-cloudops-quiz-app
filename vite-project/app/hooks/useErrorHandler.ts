import { useState, useEffect, useCallback } from 'react';
import { ErrorHandler } from '~/utils/error-handler';
import type { ErrorTypes } from '~/types';

interface Toast {
  id: string;
  message: string;
  type: ErrorTypes;
}

export function useErrorHandler() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  // エラーイベントリスナー
  useEffect(() => {
    const handleAppError = (event: CustomEvent) => {
      const { message, type } = event.detail;
      addToast(message, type);
    };

    // カスタムイベントリスナーを追加
    window.addEventListener('app-error', handleAppError as EventListener);

    return () => {
      window.removeEventListener('app-error', handleAppError as EventListener);
    };
  }, []);

  // トーストを追加
  const addToast = useCallback((message: string, type: ErrorTypes) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
    const newToast: Toast = { id, message, type };

    setToasts((prev) => [...prev, newToast]);
  }, []);

  // トーストを削除
  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  // 全てのトーストをクリア
  const clearAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  // エラーハンドリング用のヘルパー関数
  const handleNetworkError = useCallback((error: any) => {
    ErrorHandler.handleNetworkError(error);
  }, []);

  const handleDataLoadError = useCallback((error: any) => {
    ErrorHandler.handleDataLoadError(error);
  }, []);

  const handleSessionError = useCallback((error: any) => {
    ErrorHandler.handleSessionError(error);
  }, []);

  const handleValidationError = useCallback((error: any) => {
    ErrorHandler.handleValidationError(error);
  }, []);

  const handleComponentError = useCallback((error: any, errorInfo?: any) => {
    ErrorHandler.handleComponentError(error, errorInfo);
  }, []);

  // エラーログを取得
  const getErrorLogs = useCallback(() => {
    return ErrorHandler.getErrorLogs();
  }, []);

  // エラーログをクリア
  const clearErrorLogs = useCallback(() => {
    ErrorHandler.clearErrorLogs();
  }, []);

  return {
    // トースト関連
    toasts,
    addToast,
    removeToast,
    clearAllToasts,

    // エラーハンドリング関数
    handleNetworkError,
    handleDataLoadError,
    handleSessionError,
    handleValidationError,
    handleComponentError,

    // エラーログ関連
    getErrorLogs,
    clearErrorLogs,
  };
}

// 特定のエラータイプ用のカスタムフック
export function useNetworkErrorHandler() {
  const { handleNetworkError } = useErrorHandler();

  const handleFetchError = useCallback(
    async (fetchPromise: Promise<Response>) => {
      try {
        const response = await fetchPromise;
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response;
      } catch (error) {
        handleNetworkError(error);
        throw error;
      }
    },
    [handleNetworkError]
  );

  return { handleFetchError };
}

// データ読み込み用のカスタムフック
export function useDataLoader() {
  const { handleDataLoadError } = useErrorHandler();

  const loadWithErrorHandling = useCallback(
    async <T>(loader: () => Promise<T>, fallback?: T): Promise<T> => {
      try {
        return await loader();
      } catch (error) {
        handleDataLoadError(error);
        if (fallback !== undefined) {
          return fallback;
        }
        throw error;
      }
    },
    [handleDataLoadError]
  );

  return { loadWithErrorHandling };
}
