import type { SessionData } from '~/types';
import { ErrorHandler } from './error-handler';

export class SessionRecovery {
  private static readonly SESSION_KEY = 'cloudops_quiz_session';
  private static readonly BACKUP_SESSION_KEY = 'cloudops_quiz_session_backup';
  private static readonly SESSION_TIMESTAMP_KEY = 'cloudops_quiz_session_timestamp';

  /**
   * セッション復旧を試行
   */
  static attemptRecovery(): SessionData | null {
    try {
      // メインセッションを試行
      const session = this.getSession();
      
      if (session && this.validateSession(session)) {
        // セッションが有効な場合、バックアップを更新
        this.createBackup(session);
        return session;
      }

      // メインセッションが無効な場合、バックアップを試行
      const backupSession = this.getBackupSession();
      
      if (backupSession && this.validateSession(backupSession)) {
        // バックアップセッションを復元
        this.restoreFromBackup(backupSession);
        return backupSession;
      }

      // 両方とも無効な場合はクリア
      this.clearAllSessions();
      return null;

    } catch (error) {
      console.warn('Session recovery failed:', error);
      ErrorHandler.handleSessionError(error);
      this.clearAllSessions();
      return null;
    }
  }

  /**
   * セッションデータの検証
   */
  static validateSession(session: SessionData): boolean {
    try {
      // 必須フィールドの存在確認
      if (!session.sessionId || !session.startedAt || !session.mode) {
        return false;
      }

      // 配列フィールドの検証
      if (!Array.isArray(session.answers) || !Array.isArray(session.usedQuestionIds)) {
        return false;
      }

      // 日付の検証
      const startedAt = new Date(session.startedAt);
      if (isNaN(startedAt.getTime())) {
        return false;
      }

      // セッションの有効期限チェック（24時間）
      const now = new Date();
      const sessionAge = now.getTime() - startedAt.getTime();
      const maxAge = 24 * 60 * 60 * 1000; // 24時間

      if (sessionAge > maxAge) {
        console.warn('Session expired:', { sessionAge, maxAge });
        return false;
      }

      // モードの検証
      if (!['set', 'endless'].includes(session.mode)) {
        return false;
      }

      // 回答データの検証
      for (const answer of session.answers) {
        if (!answer.questionId || !answer.correctAnswer || answer.isCorrect === undefined) {
          return false;
        }
      }

      return true;

    } catch (error) {
      console.warn('Session validation failed:', error);
      return false;
    }
  }

  /**
   * セッションを取得
   */
  private static getSession(): SessionData | null {
    try {
      const data = sessionStorage.getItem(this.SESSION_KEY);
      if (!data) return null;

      const session = JSON.parse(data);
      
      // 日付文字列をDateオブジェクトに変換
      if (session.startedAt) {
        session.startedAt = new Date(session.startedAt);
      }

      if (session.answers) {
        session.answers = session.answers.map((answer: any) => ({
          ...answer,
          answeredAt: new Date(answer.answeredAt)
        }));
      }

      return session;

    } catch (error) {
      console.warn('Failed to get session:', error);
      return null;
    }
  }

  /**
   * バックアップセッションを取得
   */
  private static getBackupSession(): SessionData | null {
    try {
      const data = localStorage.getItem(this.BACKUP_SESSION_KEY);
      if (!data) return null;

      const session = JSON.parse(data);
      
      // 日付文字列をDateオブジェクトに変換
      if (session.startedAt) {
        session.startedAt = new Date(session.startedAt);
      }

      if (session.answers) {
        session.answers = session.answers.map((answer: any) => ({
          ...answer,
          answeredAt: new Date(answer.answeredAt)
        }));
      }

      return session;

    } catch (error) {
      console.warn('Failed to get backup session:', error);
      return null;
    }
  }

  /**
   * セッションのバックアップを作成
   */
  static createBackup(session: SessionData): void {
    try {
      const backupData = {
        ...session,
        startedAt: session.startedAt.toISOString(),
        answers: session.answers.map(answer => ({
          ...answer,
          answeredAt: answer.answeredAt.toISOString()
        }))
      };

      localStorage.setItem(this.BACKUP_SESSION_KEY, JSON.stringify(backupData));
      localStorage.setItem(this.SESSION_TIMESTAMP_KEY, new Date().toISOString());

    } catch (error) {
      console.warn('Failed to create session backup:', error);
    }
  }

  /**
   * バックアップからセッションを復元
   */
  private static restoreFromBackup(session: SessionData): void {
    try {
      const sessionData = {
        ...session,
        startedAt: session.startedAt.toISOString(),
        answers: session.answers.map(answer => ({
          ...answer,
          answeredAt: answer.answeredAt.toISOString()
        }))
      };

      sessionStorage.setItem(this.SESSION_KEY, JSON.stringify(sessionData));

    } catch (error) {
      console.warn('Failed to restore from backup:', error);
      ErrorHandler.handleSessionError(error);
    }
  }

  /**
   * 全てのセッションをクリア
   */
  static clearAllSessions(): void {
    try {
      sessionStorage.removeItem(this.SESSION_KEY);
      localStorage.removeItem(this.BACKUP_SESSION_KEY);
      localStorage.removeItem(this.SESSION_TIMESTAMP_KEY);
    } catch (error) {
      console.warn('Failed to clear sessions:', error);
    }
  }

  /**
   * セッション復旧の統計情報を取得
   */
  static getRecoveryStats(): {
    hasMainSession: boolean;
    hasBackupSession: boolean;
    mainSessionValid: boolean;
    backupSessionValid: boolean;
    lastBackupTime: Date | null;
  } {
    const mainSession = this.getSession();
    const backupSession = this.getBackupSession();
    
    let lastBackupTime: Date | null = null;
    try {
      const timestamp = localStorage.getItem(this.SESSION_TIMESTAMP_KEY);
      if (timestamp) {
        lastBackupTime = new Date(timestamp);
      }
    } catch (error) {
      console.warn('Failed to get backup timestamp:', error);
    }

    return {
      hasMainSession: !!mainSession,
      hasBackupSession: !!backupSession,
      mainSessionValid: mainSession ? this.validateSession(mainSession) : false,
      backupSessionValid: backupSession ? this.validateSession(backupSession) : false,
      lastBackupTime
    };
  }

  /**
   * 自動バックアップを設定
   */
  static setupAutoBackup(): void {
    // セッションストレージの変更を監視
    const originalSetItem = sessionStorage.setItem;
    
    sessionStorage.setItem = function(key: string, value: string) {
      originalSetItem.call(this, key, value);
      
      // セッションキーの変更時にバックアップを作成
      if (key === SessionRecovery.SESSION_KEY) {
        try {
          const session = JSON.parse(value);
          if (session.startedAt) {
            session.startedAt = new Date(session.startedAt);
          }
          if (session.answers) {
            session.answers = session.answers.map((answer: any) => ({
              ...answer,
              answeredAt: new Date(answer.answeredAt)
            }));
          }
          
          if (SessionRecovery.validateSession(session)) {
            SessionRecovery.createBackup(session);
          }
        } catch (error) {
          console.warn('Auto backup failed:', error);
        }
      }
    };

    // ページ離脱時にバックアップを作成
    window.addEventListener('beforeunload', () => {
      const session = this.getSession();
      if (session && this.validateSession(session)) {
        this.createBackup(session);
      }
    });

    // 定期的なバックアップ（5分間隔）
    setInterval(() => {
      const session = this.getSession();
      if (session && this.validateSession(session)) {
        this.createBackup(session);
      }
    }, 5 * 60 * 1000); // 5分
  }
}