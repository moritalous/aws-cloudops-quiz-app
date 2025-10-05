import { useState, useEffect, useCallback } from 'react';
import type { SessionData, Answer, Question, QuizStatistics } from '~/types';
import { SessionManager } from '~/utils/session-manager';
import { QuestionSelector } from '~/utils/question-selector';

export interface UseQuizSessionOptions {
  mode: 'set' | 'endless';
  targetCount?: number;
  domainFilter?: string;
  autoSave?: boolean;
}

export interface UseQuizSessionReturn {
  // セッション状態
  session: SessionData | null;
  isLoading: boolean;
  error: string | null;

  // セッション操作
  startSession: (options: UseQuizSessionOptions) => void;
  endSession: () => void;
  clearSession: () => void;
  recoverSession: () => SessionData | null;

  // 回答操作
  addAnswer: (answer: Omit<Answer, 'answeredAt'>) => void;
  updateCurrentQuestion: (index: number) => void;

  // 統計情報
  statistics: QuizStatistics | null;
  progress: {
    current: number;
    total: number | null;
    percentage: number | null;
    isComplete: boolean;
  } | null;

  // ユーティリティ
  getNextQuestion: (questions: Question[]) => Question | null;
  isQuestionUsed: (questionId: string) => boolean;
  getSessionDuration: () => number;
}

export function useQuizSession(): UseQuizSessionReturn {
  const [session, setSession] = useState<SessionData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statistics, setStatistics] = useState<QuizStatistics | null>(null);
  const [progress, setProgress] = useState<{
    current: number;
    total: number | null;
    percentage: number | null;
    isComplete: boolean;
  } | null>(null);

  // セッション状態の更新
  const updateSessionState = useCallback((newSession: SessionData | null) => {
    setSession(newSession);

    if (newSession) {
      // 統計情報を更新
      const stats = SessionManager.calculateStatistics(newSession);
      setStatistics(stats);

      // 進捗情報を更新
      const prog = SessionManager.getProgress(newSession);
      setProgress(prog);
    } else {
      setStatistics(null);
      setProgress(null);
    }
  }, []);

  // 初期化時にセッション復旧を試行
  useEffect(() => {
    const recoveredSession = SessionManager.attemptRecovery();
    if (recoveredSession) {
      updateSessionState(recoveredSession);
    }
  }, [updateSessionState]);

  // セッション開始
  const startSession = useCallback(
    (options: UseQuizSessionOptions) => {
      try {
        setIsLoading(true);
        setError(null);

        const newSession = SessionManager.createSession(
          options.mode,
          options.targetCount,
          options.domainFilter
        );

        updateSessionState(newSession);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : '不明なエラーが発生しました'
        );
      } finally {
        setIsLoading(false);
      }
    },
    [updateSessionState]
  );

  // セッション終了
  const endSession = useCallback(() => {
    if (session) {
      // セッション履歴に保存
      SessionManager.saveSessionHistory(session);

      // セッションをクリア
      SessionManager.clearSession();
      updateSessionState(null);
    }
  }, [session, updateSessionState]);

  // セッションクリア
  const clearSession = useCallback(() => {
    SessionManager.clearSession();
    updateSessionState(null);
    setError(null);
  }, [updateSessionState]);

  // セッション復旧
  const recoverSession = useCallback(() => {
    const recoveredSession = SessionManager.attemptRecovery();
    updateSessionState(recoveredSession);
    return recoveredSession;
  }, [updateSessionState]);

  // 回答追加
  const addAnswer = useCallback(
    (answerData: Omit<Answer, 'answeredAt'>) => {
      if (!session) return;

      try {
        const answer: Answer = {
          ...answerData,
          answeredAt: new Date(),
        };

        const updatedSession = SessionManager.addAnswer(answer);
        if (updatedSession) {
          updateSessionState(updatedSession);
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : '回答の保存に失敗しました'
        );
      }
    },
    [session, updateSessionState]
  );

  // 現在の問題インデックス更新
  const updateCurrentQuestion = useCallback(
    (index: number) => {
      if (!session) return;

      try {
        const updatedSession = SessionManager.updateCurrentQuestionIndex(index);
        if (updatedSession) {
          updateSessionState(updatedSession);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : '問題インデックスの更新に失敗しました'
        );
      }
    },
    [session, updateSessionState]
  );

  // 次の問題を取得
  const getNextQuestion = useCallback(
    (questions: Question[]): Question | null => {
      if (!session) return null;

      return QuestionSelector.selectRandomQuestion(
        questions,
        session.usedQuestionIds,
        session.domainFilter ? { domain: session.domainFilter } : undefined
      );
    },
    [session]
  );

  // 問題が使用済みかチェック
  const isQuestionUsed = useCallback(
    (questionId: string): boolean => {
      return session ? session.usedQuestionIds.includes(questionId) : false;
    },
    [session]
  );

  // セッション時間を取得
  const getSessionDuration = useCallback((): number => {
    return session ? SessionManager.getSessionDuration(session) : 0;
  }, [session]);

  return {
    // セッション状態
    session,
    isLoading,
    error,

    // セッション操作
    startSession,
    endSession,
    clearSession,
    recoverSession,

    // 回答操作
    addAnswer,
    updateCurrentQuestion,

    // 統計情報
    statistics,
    progress,

    // ユーティリティ
    getNextQuestion,
    isQuestionUsed,
    getSessionDuration,
  };
}

// セッション履歴を管理するフック
export function useSessionHistory() {
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadHistory = useCallback(async () => {
    setIsLoading(true);
    try {
      const sessionHistory = SessionManager.getSessionHistory();
      setHistory(sessionHistory);
    } catch (error) {
      console.error('Failed to load session history:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearHistory = useCallback(() => {
    SessionManager.clearSessionHistory();
    setHistory([]);
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  return {
    history,
    isLoading,
    loadHistory,
    clearHistory,
  };
}
