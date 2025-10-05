import type {
  Question,
  SessionData,
  Answer,
  QuizConfig,
  QuizStatistics,
} from '~/types';
import { SessionManager } from './session-manager';
import { QuestionSelector } from './question-selector';
import { loadQuestionSet } from './data-loader';

export interface QuizManagerOptions {
  balanceDomains?: boolean;
  avoidRecentQuestions?: boolean;
  preferDifficulty?: 'easy' | 'medium' | 'hard';
}

export class QuizManager {
  private questions: Question[] = [];
  private currentSession: SessionData | null = null;
  private options: QuizManagerOptions;

  constructor(options: QuizManagerOptions = {}) {
    this.options = {
      balanceDomains: true,
      avoidRecentQuestions: true,
      ...options,
    };
  }

  /**
   * 問題データを読み込み
   */
  async loadQuestions(): Promise<void> {
    const result = await loadQuestionSet();
    if (!result.success || !result.data) {
      throw new Error(result.error || 'Failed to load questions');
    }
    this.questions = result.data.questions;
  }

  /**
   * 新しいクイズセッションを開始
   */
  startNewSession(config: QuizConfig): SessionData {
    this.currentSession = SessionManager.createSession(
      config.mode,
      config.questionCount,
      config.domain
    );
    return this.currentSession;
  }

  /**
   * 既存のセッションを復旧
   */
  resumeSession(): SessionData | null {
    this.currentSession = SessionManager.attemptRecovery();
    return this.currentSession;
  }

  /**
   * 現在のセッションを取得
   */
  getCurrentSession(): SessionData | null {
    if (!this.currentSession) {
      this.currentSession = SessionManager.getSession();
    }
    return this.currentSession;
  }

  /**
   * 次の問題を取得
   */
  getNextQuestion(): Question | null {
    if (!this.currentSession || this.questions.length === 0) {
      return null;
    }

    const question = QuestionSelector.selectNextQuestion(
      this.questions,
      this.currentSession,
      {
        balanceDomains: this.options.balanceDomains,
        avoidRecentQuestions: this.options.avoidRecentQuestions,
        preferDifficulty: this.options.preferDifficulty,
      }
    );

    return question;
  }

  /**
   * 問題セットを事前生成（10問セット用）
   */
  generateQuestionSet(count: number = 10): Question[] {
    if (this.questions.length === 0) {
      return [];
    }

    const filter = this.currentSession?.domainFilter
      ? { domain: this.currentSession.domainFilter }
      : undefined;

    return QuestionSelector.selectQuestionSet(this.questions, count, filter, {
      balanceDomains: this.options.balanceDomains,
      preferDifficulty: this.options.preferDifficulty,
    });
  }

  /**
   * 回答を記録
   */
  recordAnswer(
    questionId: string,
    userAnswer: string | string[],
    correctAnswer: string | string[],
    startTime?: Date
  ): SessionData | null {
    if (!this.currentSession) {
      return null;
    }

    const now = new Date();
    const timeSpent = startTime
      ? now.getTime() - startTime.getTime()
      : undefined;

    const isCorrect = Array.isArray(correctAnswer)
      ? Array.isArray(userAnswer) &&
        correctAnswer.length === userAnswer.length &&
        correctAnswer.every((answer) => userAnswer.includes(answer))
      : userAnswer === correctAnswer;

    const answer: Answer = {
      questionId,
      userAnswer,
      correctAnswer,
      isCorrect,
      answeredAt: now,
      timeSpent,
    };

    this.currentSession = SessionManager.addAnswer(answer);
    return this.currentSession;
  }

  /**
   * 問題インデックスを更新
   */
  updateQuestionIndex(index: number): SessionData | null {
    this.currentSession = SessionManager.updateCurrentQuestionIndex(index);
    return this.currentSession;
  }

  /**
   * セッション統計を取得
   */
  getStatistics(): QuizStatistics | null {
    if (!this.currentSession) {
      return null;
    }

    const baseStats = SessionManager.calculateStatistics(this.currentSession);

    // 問題データを使用してドメイン別統計を正確に計算
    const domainBreakdown: {
      [domain: string]: { total: number; correct: number; accuracy: number };
    } = {};

    for (const answer of this.currentSession.answers) {
      const question = this.questions.find((q) => q.id === answer.questionId);
      if (question) {
        const domain = question.domain;
        if (!domainBreakdown[domain]) {
          domainBreakdown[domain] = { total: 0, correct: 0, accuracy: 0 };
        }
        domainBreakdown[domain].total++;
        if (answer.isCorrect) {
          domainBreakdown[domain].correct++;
        }
      }
    }

    // 各ドメインの正答率を計算
    for (const domain in domainBreakdown) {
      const stats = domainBreakdown[domain];
      stats.accuracy =
        stats.total > 0 ? (stats.correct / stats.total) * 100 : 0;
    }

    return {
      ...baseStats,
      domainBreakdown,
    };
  }

  /**
   * セッション要約を取得
   */
  getSessionSummary() {
    if (!this.currentSession) {
      return null;
    }
    return {
      sessionId: this.currentSession.sessionId,
      mode: this.currentSession.mode,
      startedAt: this.currentSession.startedAt,
      progress: SessionManager.getProgress(this.currentSession),
      statistics: SessionManager.calculateStatistics(this.currentSession),
      duration: SessionManager.getSessionDuration(this.currentSession),
    };
  }

  /**
   * 復習用問題を取得
   */
  getReviewQuestions(count: number = 5): Question[] {
    if (!this.currentSession) {
      return [];
    }
    return QuestionSelector.selectReviewQuestions(
      this.questions,
      this.currentSession,
      count
    );
  }

  /**
   * セッションが完了しているかチェック
   */
  isSessionComplete(): boolean {
    if (!this.currentSession) {
      return false;
    }

    if (
      this.currentSession.mode === 'set' &&
      this.currentSession.targetQuestionCount
    ) {
      return (
        this.currentSession.answers.length >=
        this.currentSession.targetQuestionCount
      );
    }

    return false; // エンドレスモードは手動終了
  }

  /**
   * 利用可能な問題数を取得
   */
  getAvailableQuestionCount(): number {
    if (!this.currentSession) {
      return this.questions.length;
    }

    const filter = this.currentSession.domainFilter
      ? { domain: this.currentSession.domainFilter }
      : undefined;

    const availableQuestions = QuestionSelector['filterQuestions'](
      this.questions,
      filter
    );
    return availableQuestions.filter(
      (q) => !this.currentSession!.usedQuestionIds.includes(q.id)
    ).length;
  }

  /**
   * 問題選択統計を取得
   */
  getSelectionStats() {
    if (!this.currentSession) {
      return null;
    }

    const filter = this.currentSession.domainFilter
      ? { domain: this.currentSession.domainFilter }
      : undefined;

    return QuestionSelector.getSelectionStats(
      this.questions,
      this.currentSession.usedQuestionIds,
      filter
    );
  }

  /**
   * セッションをクリア
   */
  clearSession(): void {
    SessionManager.clearSession();
    this.currentSession = null;
  }

  /**
   * セッションをエクスポート
   */
  exportSession(): string | null {
    const session = SessionManager.getSession();
    return session ? JSON.stringify(session) : null;
  }

  /**
   * 問題データの統計情報を取得
   */
  getQuestionDataStats() {
    return {
      totalQuestions: this.questions.length,
      difficultyDistribution: QuestionSelector.getDifficultyDistribution(
        this.questions
      ),
      domainDistribution: QuestionSelector.getDomainDistribution(
        this.questions
      ),
      duplicates: QuestionSelector.checkDuplicates(this.questions),
    };
  }

  /**
   * 特定の問題を取得
   */
  getQuestionById(questionId: string): Question | null {
    return this.questions.find((q) => q.id === questionId) || null;
  }

  /**
   * ドメイン別の問題を取得
   */
  getQuestionsByDomain(domain: string): Question[] {
    return this.questions.filter((q) => q.domain === domain);
  }

  /**
   * 難易度別の問題を取得
   */
  getQuestionsByDifficulty(difficulty: 'easy' | 'medium' | 'hard'): Question[] {
    return this.questions.filter((q) => q.difficulty === difficulty);
  }
}
