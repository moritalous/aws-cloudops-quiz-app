import type { QuestionSet, Question } from '~/types';

export interface SimpleLoadResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export class SimpleDataLoader {
  private cache = new Map<string, any>();

  /**
   * 問題セットデータを読み込む（スキーマ検証なし）
   */
  async loadQuestionSet(url: string = '/questions.json'): Promise<SimpleLoadResult<QuestionSet>> {
    try {
      // キャッシュチェック
      if (this.cache.has(url)) {
        const cachedData = this.cache.get(url);
        return {
          success: true,
          data: cachedData,
        };
      }

      // データ取得
      const response = await this.fetchWithTimeout(url, 10000);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const rawData = await response.json();

      // 基本的な構造チェック
      if (!rawData.questions || !Array.isArray(rawData.questions)) {
        throw new Error('Invalid question data format');
      }

      const questionSet = rawData as QuestionSet;

      // キャッシュに保存
      this.cache.set(url, questionSet);

      return {
        success: true,
        data: questionSet,
      };

    } catch (error) {
      return this.handleError(error, 'Failed to load question set');
    }
  }

  /**
   * ドメイン別の問題を読み込む
   */
  async loadQuestionsByDomain(domain: string): Promise<SimpleLoadResult<Question[]>> {
    try {
      const questionSetResult = await this.loadQuestionSet();
      
      if (!questionSetResult.success || !questionSetResult.data) {
        return {
          success: false,
          error: questionSetResult.error || 'Failed to load question set',
        };
      }

      const questions = questionSetResult.data.questions.filter(q => q.domain === domain);
      
      return {
        success: true,
        data: questions,
      };

    } catch (error) {
      return this.handleError(error, `Failed to load questions for domain ${domain}`);
    }
  }

  /**
   * データの再読み込み（キャッシュクリア）
   */
  async reloadQuestionSet(url: string = '/questions.json'): Promise<SimpleLoadResult<QuestionSet>> {
    this.cache.delete(url);
    return this.loadQuestionSet(url);
  }

  /**
   * キャッシュをクリア
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * タイムアウト付きfetch
   */
  private async fetchWithTimeout(url: string, timeout: number): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache',
        },
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Request timeout after ${timeout}ms`);
      }
      throw error;
    }
  }

  /**
   * エラーハンドリング
   */
  private handleError(error: unknown, defaultMessage: string): SimpleLoadResult<any> {
    let errorMessage = defaultMessage;
    
    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === 'string') {
      errorMessage = error;
    }

    // ネットワークエラーの詳細分類
    if (errorMessage.includes('Failed to fetch')) {
      errorMessage = 'ネットワーク接続に失敗しました。インターネット接続を確認してください。';
    } else if (errorMessage.includes('timeout')) {
      errorMessage = 'リクエストがタイムアウトしました。しばらく後にお試しください。';
    } else if (errorMessage.includes('404')) {
      errorMessage = '問題データファイルが見つかりません。';
    } else if (errorMessage.includes('500')) {
      errorMessage = 'サーバーエラーが発生しました。しばらく後にお試しください。';
    }

    return {
      success: false,
      error: errorMessage,
    };
  }
}

// デフォルトインスタンス
export const simpleDataLoader = new SimpleDataLoader();

// 便利な関数エクスポート
export const loadQuestionSet = (url?: string) => simpleDataLoader.loadQuestionSet(url);
export const loadQuestionsByDomain = (domain: string) => simpleDataLoader.loadQuestionsByDomain(domain);