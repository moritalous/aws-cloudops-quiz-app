import type { QuestionSet, Question } from '~/types';
import { validateQuestionSetComprehensive, type ValidationResult } from './schema-validator';
import { checkQuestionSetQuality, type QualityReport } from './question-quality-checker';

export interface LoadResult<T> {
  success: boolean;
  data?: T;
  error?: string;
  validationResult?: ValidationResult;
  qualityReport?: QualityReport;
}

export interface DataLoaderOptions {
  validateSchema?: boolean;
  checkQuality?: boolean;
  enableCache?: boolean;
  timeout?: number;
}

export class DataLoader {
  private cache = new Map<string, any>();
  private defaultOptions: DataLoaderOptions = {
    validateSchema: false, // 一時的に無効化
    checkQuality: true,
    enableCache: true,
    timeout: 10000, // 10秒
  };

  constructor(private options: DataLoaderOptions = {}) {
    this.options = { ...this.defaultOptions, ...options };
  }

  /**
   * 問題セットデータを読み込む
   */
  async loadQuestionSet(url: string = '/questions.json'): Promise<LoadResult<QuestionSet>> {
    try {
      // キャッシュチェック
      if (this.options.enableCache && this.cache.has(url)) {
        const cachedData = this.cache.get(url);
        return {
          success: true,
          data: cachedData,
        };
      }

      // データ取得
      const response = await this.fetchWithTimeout(url, this.options.timeout!);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const rawData = await response.json();

      // スキーマ検証
      let validationResult: ValidationResult | undefined;
      if (this.options.validateSchema) {
        validationResult = await validateQuestionSetComprehensive(rawData);
        if (!validationResult.isValid) {
          return {
            success: false,
            error: `Schema validation failed: ${validationResult.errors.map(e => e.message).join(', ')}`,
            validationResult,
          };
        }
      }

      const questionSet = rawData as QuestionSet;

      // 品質チェック
      let qualityReport: QualityReport | undefined;
      if (this.options.checkQuality) {
        qualityReport = checkQuestionSetQuality(questionSet);
      }

      // キャッシュに保存
      if (this.options.enableCache) {
        this.cache.set(url, questionSet);
      }

      return {
        success: true,
        data: questionSet,
        validationResult,
        qualityReport,
      };

    } catch (error) {
      return this.handleError(error, 'Failed to load question set');
    }
  }

  /**
   * 個別の問題を読み込む（将来の拡張用）
   */
  async loadQuestion(questionId: string): Promise<LoadResult<Question>> {
    try {
      // まず問題セット全体を読み込む
      const questionSetResult = await this.loadQuestionSet();
      
      if (!questionSetResult.success || !questionSetResult.data) {
        return {
          success: false,
          error: questionSetResult.error || 'Failed to load question set',
        };
      }

      const question = questionSetResult.data.questions.find(q => q.id === questionId);
      
      if (!question) {
        return {
          success: false,
          error: `Question with ID '${questionId}' not found`,
        };
      }

      return {
        success: true,
        data: question,
      };

    } catch (error) {
      return this.handleError(error, `Failed to load question ${questionId}`);
    }
  }

  /**
   * ドメイン別の問題を読み込む
   */
  async loadQuestionsByDomain(domain: string): Promise<LoadResult<Question[]>> {
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
   * 難易度別の問題を読み込む
   */
  async loadQuestionsByDifficulty(difficulty: 'easy' | 'medium' | 'hard'): Promise<LoadResult<Question[]>> {
    try {
      const questionSetResult = await this.loadQuestionSet();
      
      if (!questionSetResult.success || !questionSetResult.data) {
        return {
          success: false,
          error: questionSetResult.error || 'Failed to load question set',
        };
      }

      const questions = questionSetResult.data.questions.filter(q => q.difficulty === difficulty);
      
      return {
        success: true,
        data: questions,
      };

    } catch (error) {
      return this.handleError(error, `Failed to load ${difficulty} questions`);
    }
  }

  /**
   * フィルター条件に基づいて問題を読み込む
   */
  async loadQuestionsWithFilter(filter: {
    domain?: string;
    difficulty?: 'easy' | 'medium' | 'hard';
    type?: 'single' | 'multiple';
    tags?: string[];
  }): Promise<LoadResult<Question[]>> {
    try {
      const questionSetResult = await this.loadQuestionSet();
      
      if (!questionSetResult.success || !questionSetResult.data) {
        return {
          success: false,
          error: questionSetResult.error || 'Failed to load question set',
        };
      }

      let questions = questionSetResult.data.questions;

      // フィルター適用
      if (filter.domain) {
        questions = questions.filter(q => q.domain === filter.domain);
      }

      if (filter.difficulty) {
        questions = questions.filter(q => q.difficulty === filter.difficulty);
      }

      if (filter.type) {
        questions = questions.filter(q => q.type === filter.type);
      }

      if (filter.tags && filter.tags.length > 0) {
        questions = questions.filter(q => 
          filter.tags!.some(tag => q.tags.includes(tag))
        );
      }

      return {
        success: true,
        data: questions,
      };

    } catch (error) {
      return this.handleError(error, 'Failed to load filtered questions');
    }
  }

  /**
   * データの再読み込み（キャッシュクリア）
   */
  async reloadQuestionSet(url: string = '/questions.json'): Promise<LoadResult<QuestionSet>> {
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
   * データの健全性チェック
   */
  async validateData(url: string = '/questions.json'): Promise<ValidationResult> {
    try {
      const response = await this.fetchWithTimeout(url, this.options.timeout!);
      
      if (!response.ok) {
        return {
          isValid: false,
          errors: [{ field: 'network', message: `HTTP ${response.status}: ${response.statusText}` }]
        };
      }

      const rawData = await response.json();
      return await validateQuestionSetComprehensive(rawData);

    } catch (error) {
      return {
        isValid: false,
        errors: [{ field: 'network', message: error instanceof Error ? error.message : 'Unknown error' }]
      };
    }
  }

  /**
   * データの品質レポート取得
   */
  async getQualityReport(url: string = '/questions.json'): Promise<QualityReport | null> {
    try {
      const result = await this.loadQuestionSet(url);
      return result.qualityReport || null;
    } catch {
      return null;
    }
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
  private handleError(error: unknown, defaultMessage: string): LoadResult<any> {
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
export const defaultDataLoader = new DataLoader();

// 便利な関数エクスポート
export const loadQuestionSet = (url?: string) => defaultDataLoader.loadQuestionSet(url);
export const loadQuestion = (questionId: string) => defaultDataLoader.loadQuestion(questionId);
export const loadQuestionsByDomain = (domain: string) => defaultDataLoader.loadQuestionsByDomain(domain);
export const loadQuestionsByDifficulty = (difficulty: 'easy' | 'medium' | 'hard') => 
  defaultDataLoader.loadQuestionsByDifficulty(difficulty);
export const loadQuestionsWithFilter = (filter: Parameters<DataLoader['loadQuestionsWithFilter']>[0]) => 
  defaultDataLoader.loadQuestionsWithFilter(filter);