import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SessionManager } from '../session-manager';
import type { SessionData, Answer } from '~/types';

// Mock sessionStorage
const mockSessionStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'sessionStorage', {
  value: mockSessionStorage,
});

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

describe('SessionManager', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createSession', () => {
    it('should create a new session with correct properties', () => {
      const session = SessionManager.createSession('set', 10);

      expect(session.sessionId).toBeDefined();
      expect(session.mode).toBe('set');
      expect(session.targetQuestionCount).toBe(10);
      expect(session.currentQuestionIndex).toBe(0);
      expect(session.answers).toEqual([]);
      expect(session.usedQuestionIds).toEqual([]);
      expect(session.startedAt).toBeInstanceOf(Date);
      expect(mockSessionStorage.setItem).toHaveBeenCalled();
    });

    it('should create endless mode session', () => {
      const session = SessionManager.createSession('endless');

      expect(session.mode).toBe('endless');
      expect(session.targetQuestionCount).toBeUndefined();
    });

    it('should create session with domain filter', () => {
      const session = SessionManager.createSession('set', 10, 'monitoring');

      expect(session.domainFilter).toBe('monitoring');
    });
  });

  describe('getSession', () => {
    it('should return null when no session exists', () => {
      mockSessionStorage.getItem.mockReturnValue(null);

      const session = SessionManager.getSession();

      expect(session).toBeNull();
    });

    it('should return parsed session data', () => {
      const mockSessionData = {
        sessionId: 'test-session',
        startedAt: new Date().toISOString(),
        mode: 'set',
        targetQuestionCount: 10,
        currentQuestionIndex: 0,
        answers: [
          {
            questionId: 'q1',
            userAnswer: 'A',
            correctAnswer: 'A',
            isCorrect: true,
            answeredAt: new Date().toISOString(),
          },
        ],
        usedQuestionIds: ['q1'],
      };

      mockSessionStorage.getItem.mockReturnValue(
        JSON.stringify(mockSessionData)
      );

      const session = SessionManager.getSession();

      expect(session).toBeDefined();
      expect(session?.sessionId).toBe('test-session');
      expect(session?.startedAt).toBeInstanceOf(Date);
      expect(session?.answers[0].answeredAt).toBeInstanceOf(Date);
    });

    it('should handle corrupted session data', () => {
      mockSessionStorage.getItem.mockReturnValue('invalid-json');

      const session = SessionManager.getSession();

      expect(session).toBeNull();
      expect(mockSessionStorage.removeItem).toHaveBeenCalled();
    });
  });

  describe('addAnswer', () => {
    it('should add answer to existing session', () => {
      const mockSession: SessionData = {
        sessionId: 'test-session',
        startedAt: new Date(),
        mode: 'set',
        targetQuestionCount: 10,
        currentQuestionIndex: 0,
        answers: [],
        usedQuestionIds: [],
      };

      mockSessionStorage.getItem.mockReturnValue(JSON.stringify(mockSession));

      const answer: Answer = {
        questionId: 'q1',
        userAnswer: 'A',
        correctAnswer: 'A',
        isCorrect: true,
        answeredAt: new Date(),
      };

      const updatedSession = SessionManager.addAnswer(answer);

      expect(updatedSession).toBeDefined();
      expect(updatedSession?.answers).toHaveLength(1);
      expect(updatedSession?.usedQuestionIds).toContain('q1');
      expect(mockSessionStorage.setItem).toHaveBeenCalled();
    });

    it('should return null when no session exists', () => {
      mockSessionStorage.getItem.mockReturnValue(null);

      const answer: Answer = {
        questionId: 'q1',
        userAnswer: 'A',
        correctAnswer: 'A',
        isCorrect: true,
        answeredAt: new Date(),
      };

      const result = SessionManager.addAnswer(answer);

      expect(result).toBeNull();
    });
  });

  describe('calculateStatistics', () => {
    it('should calculate correct statistics', () => {
      const session: SessionData = {
        sessionId: 'test-session',
        startedAt: new Date(),
        mode: 'set',
        targetQuestionCount: 3,
        currentQuestionIndex: 3,
        answers: [
          {
            questionId: 'q1',
            userAnswer: 'A',
            correctAnswer: 'A',
            isCorrect: true,
            answeredAt: new Date(),
            timeSpent: 30,
          },
          {
            questionId: 'q2',
            userAnswer: 'B',
            correctAnswer: 'A',
            isCorrect: false,
            answeredAt: new Date(),
            timeSpent: 45,
          },
          {
            questionId: 'q3',
            userAnswer: 'C',
            correctAnswer: 'C',
            isCorrect: true,
            answeredAt: new Date(),
            timeSpent: 25,
          },
        ],
        usedQuestionIds: ['q1', 'q2', 'q3'],
      };

      const stats = SessionManager.calculateStatistics(session);

      expect(stats.totalQuestions).toBe(3);
      expect(stats.correctAnswers).toBe(2);
      expect(stats.accuracy).toBeCloseTo(66.67, 2);
      expect(stats.averageTimePerQuestion).toBeCloseTo(33.33, 2);
    });

    it('should handle empty answers array', () => {
      const session: SessionData = {
        sessionId: 'test-session',
        startedAt: new Date(),
        mode: 'set',
        targetQuestionCount: 10,
        currentQuestionIndex: 0,
        answers: [],
        usedQuestionIds: [],
      };

      const stats = SessionManager.calculateStatistics(session);

      expect(stats.totalQuestions).toBe(0);
      expect(stats.correctAnswers).toBe(0);
      expect(stats.accuracy).toBe(0);
    });
  });

  describe('validateSession', () => {
    it('should validate correct session data', () => {
      const validSession: SessionData = {
        sessionId: 'test-session',
        startedAt: new Date(),
        mode: 'set',
        targetQuestionCount: 10,
        currentQuestionIndex: 0,
        answers: [],
        usedQuestionIds: [],
      };

      const isValid = SessionManager.validateSession(validSession);

      expect(isValid).toBe(true);
    });

    it('should reject invalid session data', () => {
      const invalidSession = {
        sessionId: '',
        startedAt: 'invalid-date',
        mode: 'set',
        answers: 'not-array',
        usedQuestionIds: [],
      } as any;

      const isValid = SessionManager.validateSession(invalidSession);

      expect(isValid).toBe(false);
    });
  });

  describe('getProgress', () => {
    it('should calculate progress for set mode', () => {
      const session: SessionData = {
        sessionId: 'test-session',
        startedAt: new Date(),
        mode: 'set',
        targetQuestionCount: 10,
        currentQuestionIndex: 3,
        answers: [
          {
            questionId: 'q1',
            userAnswer: 'A',
            correctAnswer: 'A',
            isCorrect: true,
            answeredAt: new Date(),
          },
          {
            questionId: 'q2',
            userAnswer: 'B',
            correctAnswer: 'A',
            isCorrect: false,
            answeredAt: new Date(),
          },
          {
            questionId: 'q3',
            userAnswer: 'C',
            correctAnswer: 'C',
            isCorrect: true,
            answeredAt: new Date(),
          },
        ],
        usedQuestionIds: ['q1', 'q2', 'q3'],
      };

      const progress = SessionManager.getProgress(session);

      expect(progress.current).toBe(3);
      expect(progress.total).toBe(10);
      expect(progress.percentage).toBe(30);
      expect(progress.isComplete).toBe(false);
    });

    it('should handle endless mode', () => {
      const session: SessionData = {
        sessionId: 'test-session',
        startedAt: new Date(),
        mode: 'endless',
        currentQuestionIndex: 5,
        answers: Array(5)
          .fill(null)
          .map((_, i) => ({
            questionId: `q${i}`,
            userAnswer: 'A',
            correctAnswer: 'A',
            isCorrect: true,
            answeredAt: new Date(),
          })),
        usedQuestionIds: ['q0', 'q1', 'q2', 'q3', 'q4'],
      };

      const progress = SessionManager.getProgress(session);

      expect(progress.current).toBe(5);
      expect(progress.total).toBeNull();
      expect(progress.percentage).toBeNull();
      expect(progress.isComplete).toBe(false);
    });
  });

  describe('clearSession', () => {
    it('should clear session storage', () => {
      SessionManager.clearSession();

      expect(mockSessionStorage.removeItem).toHaveBeenCalledWith(
        'cloudops_quiz_session'
      );
    });
  });
});
