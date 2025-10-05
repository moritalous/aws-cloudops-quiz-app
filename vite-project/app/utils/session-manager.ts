import type { SessionData, Answer, QuizStatistics } from '~/types';

export class SessionManager {
  private static readonly SESSION_KEY = 'cloudops_quiz_session';
  private static readonly STATS_KEY = 'cloudops_quiz_stats';

  /**
   * 新しいセッションを作成する
   */
  static createSession(
    mode: 'set' | 'endless',
    targetCount?: number,
    domainFilter?: string
  ): SessionData {
    const session: SessionData = {
      sessionId: this.generateSessionId(),
      startedAt: new Date(),
      mode,
      targetQuestionCount: targetCount,
      currentQuestionIndex: 0,
      answers: [],
      usedQuestionIds: [],
      domainFilter,
    };

    this.saveSession(session);
    return session;
  }

  /**
   * 現在のセッションを取得する
   */
  static getSession(): SessionData | null {
    try {
      const data = sessionStorage.getItem(this.SESSION_KEY);
      if (!data) return null;

      const session = JSON.parse(data);
      // Date オブジェクトを復元
      session.startedAt = new Date(session.startedAt);
      session.answers = session.answers.map((answer: any) => ({
        ...answer,
        answeredAt: new Date(answer.answeredAt),
      }));

      return session;
    } catch (error) {
      console.warn('Failed to parse session data:', error);
      this.clearSession();
      return null;
    }
  }

  /**
   * セッションを保存する
   */
  static saveSession(session: SessionData): void {
    try {
      sessionStorage.setItem(this.SESSION_KEY, JSON.stringify(session));
    } catch (error) {
      console.error('Failed to save session:', error);
    }
  }

  /**
   * セッションを更新する
   */
  static updateSession(updates: Partial<SessionData>): SessionData | null {
    const currentSession = this.getSession();
    if (!currentSession) return null;

    const updatedSession = { ...currentSession, ...updates };
    this.saveSession(updatedSession);
    return updatedSession;
  }

  /**
   * セッションをクリアする
   */
  static clearSession(): void {
    sessionStorage.removeItem(this.SESSION_KEY);
  }

  /**
   * 回答を追加する
   */
  static addAnswer(answer: Answer): SessionData | null {
    const session = this.getSession();
    if (!session) return null;

    const updatedAnswers = [...session.answers, answer];
    const updatedSession = {
      ...session,
      answers: updatedAnswers,
      usedQuestionIds: [...session.usedQuestionIds, answer.questionId],
    };

    this.saveSession(updatedSession);
    return updatedSession;
  }

  /**
   * 現在の問題インデックスを更新する
   */
  static updateCurrentQuestionIndex(index: number): SessionData | null {
    return this.updateSession({ currentQuestionIndex: index });
  }

  /**
   * セッション統計を計算する
   */
  static calculateStatistics(session: SessionData): QuizStatistics {
    const { answers } = session;
    const correctAnswers = answers.filter((a) => a.isCorrect).length;
    const totalQuestions = answers.length;
    const accuracy = totalQuestions > 0 ? (correctAnswers / totalQuestions) * 100 : 0;

    // ドメイン別統計を計算（問題データが必要なため、ここでは基本統計のみ）
    const domainBreakdown: {
      [domain: string]: {
        total: number;
        correct: number;
        accuracy: number;
      };
    } = {};

    // 時間統計を計算
    let averageTimePerQuestion: number | undefined;
    if (answers.length > 0 && answers.some((a) => a.timeSpent)) {
      const totalTime = answers
        .filter((a) => a.timeSpent)
        .reduce((sum, a) => sum + (a.timeSpent || 0), 0);
      const questionsWithTime = answers.filter((a) => a.timeSpent).length;
      averageTimePerQuestion = questionsWithTime > 0 ? totalTime / questionsWithTime : undefined;
    }

    return {
      totalQuestions,
      correctAnswers,
      accuracy,
      domainBreakdown,
      averageTimePerQuestion,
    };
  }

  /**
   * ドメイン別統計を計算する（問題データを使用）
   */
  static calculateDomainStatistics(
    session: SessionData,
    questionMap: Map<string, { domain: string }>
  ): QuizStatistics {
    const stats = this.calculateStatistics(session);
    const domainBreakdown: {
      [domain: string]: {
        total: number;
        correct: number;
        accuracy: number;
      };
    } = {};

    // ドメイン別に集計
    session.answers.forEach((answer) => {
      const questionData = questionMap.get(answer.questionId);
      if (questionData) {
        const domain = questionData.domain;
        if (!domainBreakdown[domain]) {
          domainBreakdown[domain] = { total: 0, correct: 0, accuracy: 0 };
        }
        domainBreakdown[domain].total++;
        if (answer.isCorrect) {
          domainBreakdown[domain].correct++;
        }
      }
    });

    // 正答率を計算
    Object.keys(domainBreakdown).forEach((domain) => {
      const domainStats = domainBreakdown[domain];
      domainStats.accuracy =
        domainStats.total > 0 ? (domainStats.correct / domainStats.total) * 100 : 0;
    });

    return {
      ...stats,
      domainBreakdown,
    };
  }

  /**
   * セッションの有効性をチェックする
   */
  static validateSession(session: SessionData): boolean {
    try {
      return (
        session.sessionId &&
        session.startedAt instanceof Date &&
        session.mode &&
        Array.isArray(session.answers) &&
        Array.isArray(session.usedQuestionIds) &&
        typeof session.currentQuestionIndex === 'number'
      );
    } catch {
      return false;
    }
  }

  /**
   * セッション復旧を試行する
   */
  static attemptRecovery(): SessionData | null {
    try {
      const session = this.getSession();
      if (!session) return null;

      if (this.validateSession(session)) {
        return session;
      } else {
        console.warn('Invalid session data found, clearing...');
        this.clearSession();
        return null;
      }
    } catch (error) {
      console.warn('Session recovery failed:', error);
      this.clearSession();
      return null;
    }
  }

  /**
   * セッションの進捗状況を取得する
   */
  static getProgress(session: SessionData): {
    current: number;
    total: number | null;
    percentage: number | null;
    isComplete: boolean;
  } {
    const current = session.answers.length;
    const total = session.targetQuestionCount || null;
    const percentage = total ? (current / total) * 100 : null;
    const isComplete = total ? current >= total : false;

    return {
      current,
      total,
      percentage,
      isComplete,
    };
  }

  /**
   * セッション時間を計算する
   */
  static getSessionDuration(session: SessionData): number {
    const now = new Date();
    const startTime = session.startedAt;
    return Math.floor((now.getTime() - startTime.getTime()) / 1000); // 秒単位
  }

  /**
   * セッション履歴を保存する（完了時）
   */
  static saveSessionHistory(session: SessionData): void {
    try {
      const history = this.getSessionHistory();
      const sessionSummary = {
        sessionId: session.sessionId,
        mode: session.mode,
        startedAt: session.startedAt,
        completedAt: new Date(),
        statistics: this.calculateStatistics(session),
        duration: this.getSessionDuration(session),
      };

      history.push(sessionSummary);

      // 最新の10セッションのみ保持
      const recentHistory = history.slice(-10);
      localStorage.setItem(this.STATS_KEY, JSON.stringify(recentHistory));
    } catch (error) {
      console.error('Failed to save session history:', error);
    }
  }

  /**
   * セッション履歴を取得する
   */
  static getSessionHistory(): any[] {
    try {
      const data = localStorage.getItem(this.STATS_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  /**
   * セッション履歴をクリアする
   */
  static clearSessionHistory(): void {
    localStorage.removeItem(this.STATS_KEY);
  }

  /**
   * ユニークなセッションIDを生成する
   */
  private static generateSessionId(): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    return `session_${timestamp}_${random}`;
  }

  /**
   * セッションのデバッグ情報を出力する
   */
  static debugSession(): void {
    const session = this.getSession();
    if (session) {
      console.log('Current Session:', {
        id: session.sessionId,
        mode: session.mode,
        startedAt: session.startedAt,
        progress: this.getProgress(session),
        duration: this.getSessionDuration(session),
        statistics: this.calculateStatistics(session),
      });
    } else {
      console.log('No active session');
    }
  }
}