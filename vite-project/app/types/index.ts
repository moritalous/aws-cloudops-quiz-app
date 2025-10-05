// AWS CloudOps試験対策アプリの型定義

export interface Question {
  id: string;
  domain: string;
  difficulty: 'easy' | 'medium' | 'hard';
  type: 'single' | 'multiple';
  question: string;
  options: string[];
  correctAnswer: string | string[];
  explanation: string;
  learningResources: LearningResource[];
  relatedServices: string[];
  tags: string[];
}

export interface LearningResource {
  title: string;
  url: string;
  type: 'documentation' | 'blog' | 'video' | 'whitepaper';
  description?: string;
}

export interface QuestionSet {
  version: string;
  generatedAt: string;
  totalQuestions: number;
  domains: {
    [domain: string]: number;
  };
  questions: Question[];
}

export interface SessionData {
  sessionId: string;
  startedAt: Date;
  mode: 'set' | 'endless';
  targetQuestionCount?: number;
  currentQuestionIndex: number;
  answers: Answer[];
  usedQuestionIds: string[];
  domainFilter?: string;
}

export interface Answer {
  questionId: string;
  userAnswer: string | string[];
  correctAnswer: string | string[];
  isCorrect: boolean;
  answeredAt: Date;
  timeSpent?: number;
}

export interface QuizStatistics {
  totalQuestions: number;
  correctAnswers: number;
  accuracy: number;
  domainBreakdown: {
    [domain: string]: {
      total: number;
      correct: number;
      accuracy: number;
    };
  };
  averageTimePerQuestion?: number;
}

export interface QuizConfig {
  mode: 'set' | 'endless';
  domain?: string;
  questionCount: number;
}

export interface AppError {
  type: ErrorTypes;
  message: string;
  details?: any;
  timestamp: Date;
}

export enum ErrorTypes {
  NETWORK_ERROR = 'NETWORK_ERROR',
  DATA_LOAD_ERROR = 'DATA_LOAD_ERROR',
  SESSION_ERROR = 'SESSION_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR'
}