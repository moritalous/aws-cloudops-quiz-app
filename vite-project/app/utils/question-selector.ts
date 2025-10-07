import type { Question, SessionData } from '~/types';

export interface QuestionFilter {
  domain?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  type?: 'single' | 'multiple';
  tags?: string[];
  excludeIds?: string[];
}

export interface SelectionOptions {
  avoidRecentQuestions?: boolean;
  recentQuestionWindow?: number; // 最近の問題を避ける範囲（問題数）
  balanceDomains?: boolean;
  preferDifficulty?: 'easy' | 'medium' | 'hard';
  maxRetries?: number;
}

export class QuestionSelector {
  /**
   * ランダムに問題を選択
   */
  static selectRandomQuestion(
    questions: Question[],
    usedQuestionIds: string[] = [],
    filter?: QuestionFilter,
    options: SelectionOptions = {}
  ): Question | null {
    const {
      avoidRecentQuestions = true,
      recentQuestionWindow = 5,
      maxRetries = 3,
    } = options;

    // フィルタリング
    let availableQuestions = this.filterQuestions(questions, filter);

    // 使用済み問題を除外
    availableQuestions = availableQuestions.filter(
      (q) => !usedQuestionIds.includes(q.id)
    );

    // 最近の問題を避ける
    if (avoidRecentQuestions && usedQuestionIds.length > 0) {
      const recentIds = usedQuestionIds.slice(-recentQuestionWindow);
      availableQuestions = availableQuestions.filter(
        (q) => !recentIds.includes(q.id)
      );
    }

    // 利用可能な問題がない場合の処理
    if (availableQuestions.length === 0) {
      // 使用済み問題をリセットして再試行
      availableQuestions = this.filterQuestions(questions, filter);

      if (availableQuestions.length === 0) {
        return null; // フィルター条件に合う問題が存在しない
      }
    }

    // 難易度の優先度を適用
    if (options.preferDifficulty) {
      const preferredQuestions = availableQuestions.filter(
        (q) => q.difficulty === options.preferDifficulty
      );
      if (preferredQuestions.length > 0) {
        availableQuestions = preferredQuestions;
      }
    }

    // ランダム選択
    const randomIndex = Math.floor(Math.random() * availableQuestions.length);
    return availableQuestions[randomIndex];
  }

  /**
   * 問題セットを選択（10問セット用）
   */
  static selectQuestionSet(
    questions: Question[],
    count: number,
    filter?: QuestionFilter,
    options: SelectionOptions = {}
  ): Question[] {
    const { balanceDomains = true } = options;
    const selectedQuestions: Question[] = [];
    const usedIds: string[] = [];

    if (balanceDomains && !filter?.domain) {
      // ドメインバランスを考慮した選択
      return this.selectBalancedQuestionSet(questions, count, filter, options);
    }

    // 通常の選択
    for (let i = 0; i < count; i++) {
      const question = this.selectRandomQuestion(
        questions,
        usedIds,
        filter,
        options
      );
      if (question) {
        selectedQuestions.push(question);
        usedIds.push(question.id);
      } else {
        // 選択できる問題がない場合は終了
        break;
      }
    }

    return selectedQuestions;
  }

  /**
   * ドメインバランスを考慮した問題セット選択
   */
  static selectBalancedQuestionSet(
    questions: Question[],
    count: number,
    filter?: QuestionFilter,
    options: SelectionOptions = {}
  ): Question[] {
    const selectedQuestions: Question[] = [];
    const usedIds: string[] = [];

    // 利用可能なドメインを取得
    const availableQuestions = this.filterQuestions(questions, filter);
    const domains = [...new Set(availableQuestions.map((q) => q.domain))];

    if (domains.length === 0) return [];

    // 各ドメインから選択する問題数を計算
    const questionsPerDomain = Math.floor(count / domains.length);
    const remainder = count % domains.length;

    // 各ドメインから問題を選択
    for (let i = 0; i < domains.length; i++) {
      const domain = domains[i];
      const domainQuestionCount = questionsPerDomain + (i < remainder ? 1 : 0);

      const domainFilter = { ...filter, domain };

      for (let j = 0; j < domainQuestionCount; j++) {
        const question = this.selectRandomQuestion(
          questions,
          usedIds,
          domainFilter,
          options
        );

        if (question) {
          selectedQuestions.push(question);
          usedIds.push(question.id);
        }
      }
    }

    // 不足分をランダムに補完
    while (selectedQuestions.length < count) {
      const question = this.selectRandomQuestion(
        questions,
        usedIds,
        filter,
        options
      );
      if (question) {
        selectedQuestions.push(question);
        usedIds.push(question.id);
      } else {
        break;
      }
    }

    // シャッフル
    return this.shuffleArray(selectedQuestions);
  }

  /**
   * セッションに基づいて次の問題を選択
   */
  static selectNextQuestion(
    questions: Question[],
    session: SessionData,
    options: SelectionOptions = {}
  ): Question | null {
    const filter: QuestionFilter = {
      domain: session.domainFilter,
    };

    return this.selectRandomQuestion(
      questions,
      session.usedQuestionIds,
      filter,
      options
    );
  }

  /**
   * 復習用の問題を選択（間違えた問題から）
   */
  static selectReviewQuestions(
    questions: Question[],
    session: SessionData,
    count: number = 5
  ): Question[] {
    // 間違えた問題のIDを取得
    const incorrectAnswers = session.answers.filter((a) => !a.isCorrect);
    const incorrectQuestionIds = incorrectAnswers.map((a) => a.questionId);

    // 間違えた問題を取得
    const incorrectQuestions = questions.filter((q) =>
      incorrectQuestionIds.includes(q.id)
    );

    // 最大count個まで選択
    const selectedCount = Math.min(count, incorrectQuestions.length);
    return this.shuffleArray(incorrectQuestions).slice(0, selectedCount);
  }

  /**
   * 難易度別の問題分布を取得
   */
  static getDifficultyDistribution(questions: Question[]): {
    easy: number;
    medium: number;
    hard: number;
    total: number;
  } {
    const distribution = {
      easy: 0,
      medium: 0,
      hard: 0,
      total: questions.length,
    };

    for (const question of questions) {
      distribution[question.difficulty]++;
    }

    return distribution;
  }

  /**
   * ドメイン別の問題分布を取得
   */
  static getDomainDistribution(questions: Question[]): {
    [domain: string]: number;
  } {
    const distribution: { [domain: string]: number } = {};

    for (const question of questions) {
      distribution[question.domain] = (distribution[question.domain] || 0) + 1;
    }

    return distribution;
  }

  /**
   * 問題をフィルタリング
   */
  private static filterQuestions(
    questions: Question[],
    filter?: QuestionFilter
  ): Question[] {
    if (!filter) return questions;

    return questions.filter((question) => {
      // ドメインフィルター
      if (filter.domain && question.domain !== filter.domain) {
        return false;
      }

      // 難易度フィルター
      if (filter.difficulty && question.difficulty !== filter.difficulty) {
        return false;
      }

      // タイプフィルター
      if (filter.type && question.type !== filter.type) {
        return false;
      }

      // タグフィルター
      if (filter.tags && filter.tags.length > 0) {
        const hasMatchingTag = filter.tags.some((tag) =>
          question.tags.includes(tag)
        );
        if (!hasMatchingTag) {
          return false;
        }
      }

      // 除外IDフィルター
      if (filter.excludeIds && filter.excludeIds.includes(question.id)) {
        return false;
      }

      return true;
    });
  }

  /**
   * 配列をシャッフル（Fisher-Yates アルゴリズム）
   */
  static shuffleArray<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  /**
   * 問題の重複チェック
   */
  static checkDuplicates(questions: Question[]): string[] {
    const ids = questions.map((q) => q.id);
    const duplicates: string[] = [];
    const seen = new Set<string>();

    for (const id of ids) {
      if (seen.has(id)) {
        duplicates.push(id);
      } else {
        seen.add(id);
      }
    }

    return duplicates;
  }

  /**
   * 問題選択の統計情報を取得
   */
  static getSelectionStats(
    questions: Question[],
    usedQuestionIds: string[],
    filter?: QuestionFilter
  ): {
    totalQuestions: number;
    availableQuestions: number;
    usedQuestions: number;
    usagePercentage: number;
    domainBreakdown: {
      [domain: string]: { total: number; used: number; available: number };
    };
  } {
    const filteredQuestions = this.filterQuestions(questions, filter);
    const availableQuestions = filteredQuestions.filter(
      (q) => !usedQuestionIds.includes(q.id)
    );

    const domainBreakdown: {
      [domain: string]: { total: number; used: number; available: number };
    } = {};

    for (const question of filteredQuestions) {
      if (!domainBreakdown[question.domain]) {
        domainBreakdown[question.domain] = { total: 0, used: 0, available: 0 };
      }

      domainBreakdown[question.domain].total++;

      if (usedQuestionIds.includes(question.id)) {
        domainBreakdown[question.domain].used++;
      } else {
        domainBreakdown[question.domain].available++;
      }
    }

    return {
      totalQuestions: filteredQuestions.length,
      availableQuestions: availableQuestions.length,
      usedQuestions: usedQuestionIds.length,
      usagePercentage:
        filteredQuestions.length > 0
          ? (usedQuestionIds.length / filteredQuestions.length) * 100
          : 0,
      domainBreakdown,
    };
  }
}
