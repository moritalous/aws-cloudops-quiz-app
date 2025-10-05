import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SessionManager } from '../session-manager';
import { QuestionSelector } from '../question-selector';
import type { Question, SessionData } from '~/types';

// Mock storage with actual storage behavior
const mockStorage = new Map<string, string>();

const mockSessionStorage = {
  getItem: vi.fn((key: string) => mockStorage.get(key) || null),
  setItem: vi.fn((key: string, value: string) => mockStorage.set(key, value)),
  removeItem: vi.fn((key: string) => mockStorage.delete(key)),
  clear: vi.fn(() => mockStorage.clear()),
};

Object.defineProperty(window, 'sessionStorage', {
  value: mockSessionStorage,
});

const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

describe('SessionManager + QuestionSelector Integration', () => {
  const mockQuestions: Question[] = [
    {
      id: 'q1',
      domain: 'monitoring',
      difficulty: 'medium',
      type: 'single',
      question: 'Which service monitors AWS resources?',
      options: ['A. CloudWatch', 'B. CloudTrail', 'C. Config', 'D. Inspector'],
      correctAnswer: 'A',
      explanation: 'CloudWatch monitors AWS resources.',
      learningResources: [],
      relatedServices: ['CloudWatch'],
      tags: ['monitoring']
    },
    {
      id: 'q2',
      domain: 'security',
      difficulty: 'hard',
      type: 'single',
      question: 'Which service provides identity management?',
      options: ['A. IAM', 'B. Cognito', 'C. Directory Service', 'D. SSO'],
      correctAnswer: 'A',
      explanation: 'IAM provides identity and access management.',
      learningResources: [],
      relatedServices: ['IAM'],
      tags: ['security', 'identity']
    },
    {
      id: 'q3',
      domain: 'monitoring',
      difficulty: 'easy',
      type: 'single',
      question: 'What is CloudWatch used for?',
      options: ['A. Monitoring', 'B. Storage', 'C. Compute', 'D. Networking'],
      correctAnswer: 'A',
      explanation: 'CloudWatch is used for monitoring.',
      learningResources: [],
      relatedServices: ['CloudWatch'],
      tags: ['monitoring', 'basics']
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    mockStorage.clear();
  });

  it('should create session and select questions without duplicates', () => {
    // Create a new session
    const session = SessionManager.createSession('set', 2, 'monitoring');
    expect(session.usedQuestionIds).toHaveLength(0);

    // Select first question
    const question1 = QuestionSelector.selectNextQuestion(mockQuestions, session);
    expect(question1).toBeDefined();
    expect(question1?.domain).toBe('monitoring');

    // Add answer and update session
    if (question1) {
      const updatedSession = SessionManager.addAnswer({
        questionId: question1.id,
        userAnswer: 'A',
        correctAnswer: question1.correctAnswer,
        isCorrect: true,
        answeredAt: new Date()
      });

      expect(updatedSession?.usedQuestionIds).toContain(question1.id);

      // Select second question - should be different
      const question2 = QuestionSelector.selectNextQuestion(mockQuestions, updatedSession!);
      expect(question2).toBeDefined();
      expect(question2?.id).not.toBe(question1.id);
      expect(question2?.domain).toBe('monitoring');
    }
  });

  it('should handle question set selection with session tracking', () => {
    // Create session
    const session = SessionManager.createSession('set', 10);

    // Select a balanced question set
    const questionSet = QuestionSelector.selectQuestionSet(mockQuestions, 3, undefined, {
      balanceDomains: true
    });

    expect(questionSet).toHaveLength(3);

    // Simulate answering all questions
    let currentSession = session;
    questionSet.forEach((question, index) => {
      const answer = {
        questionId: question.id,
        userAnswer: 'A',
        correctAnswer: question.correctAnswer,
        isCorrect: Math.random() > 0.5, // Random correct/incorrect
        answeredAt: new Date(),
        timeSpent: 30 + Math.random() * 30
      };

      const updatedSession = SessionManager.addAnswer(answer);
      expect(updatedSession).toBeDefined();
      currentSession = updatedSession!;
    });

    // Check final statistics
    const stats = SessionManager.calculateStatistics(currentSession);
    expect(stats.totalQuestions).toBe(3);
    expect(stats.correctAnswers).toBeGreaterThanOrEqual(0);
    expect(stats.correctAnswers).toBeLessThanOrEqual(3);

    // Check progress
    const progress = SessionManager.getProgress(currentSession);
    expect(progress.current).toBe(3);
    expect(progress.total).toBe(10);
    expect(progress.percentage).toBe(30);
  });

  it('should handle domain filtering correctly', () => {
    // Create session with domain filter
    const session = SessionManager.createSession('set', 5, 'monitoring');

    // Select questions with domain filter
    const monitoringQuestions = QuestionSelector.selectQuestionSet(
      mockQuestions, 
      2, 
      { domain: 'monitoring' }
    );

    expect(monitoringQuestions).toHaveLength(2);
    monitoringQuestions.forEach(q => {
      expect(q.domain).toBe('monitoring');
    });

    // Verify no duplicates
    const questionIds = monitoringQuestions.map(q => q.id);
    const uniqueIds = [...new Set(questionIds)];
    expect(uniqueIds).toHaveLength(questionIds.length);
  });

  it('should calculate domain statistics correctly', () => {
    // Create session and add mixed domain answers
    const session = SessionManager.createSession('endless');
    
    // Add answers from different domains
    let currentSession = session;
    const answers = [
      { questionId: 'q1', domain: 'monitoring', isCorrect: true },
      { questionId: 'q2', domain: 'security', isCorrect: false },
      { questionId: 'q3', domain: 'monitoring', isCorrect: true }
    ];

    answers.forEach(answerData => {
      const updatedSession = SessionManager.addAnswer({
        questionId: answerData.questionId,
        userAnswer: 'A',
        correctAnswer: answerData.isCorrect ? 'A' : 'B',
        isCorrect: answerData.isCorrect,
        answeredAt: new Date()
      });
      currentSession = updatedSession!;
    });

    // Create question map for domain statistics
    const questionMap = new Map([
      ['q1', { domain: 'monitoring' }],
      ['q2', { domain: 'security' }],
      ['q3', { domain: 'monitoring' }]
    ]);

    const domainStats = SessionManager.calculateDomainStatistics(currentSession, questionMap);
    
    expect(domainStats.domainBreakdown.monitoring).toBeDefined();
    expect(domainStats.domainBreakdown.monitoring.total).toBe(2);
    expect(domainStats.domainBreakdown.monitoring.correct).toBe(2);
    expect(domainStats.domainBreakdown.monitoring.accuracy).toBe(100);

    expect(domainStats.domainBreakdown.security).toBeDefined();
    expect(domainStats.domainBreakdown.security.total).toBe(1);
    expect(domainStats.domainBreakdown.security.correct).toBe(0);
    expect(domainStats.domainBreakdown.security.accuracy).toBe(0);
  });

  it('should handle session recovery after corruption', () => {
    // Create and save a session
    const originalSession = SessionManager.createSession('set', 10);
    SessionManager.addAnswer({
      questionId: 'q1',
      userAnswer: 'A',
      correctAnswer: 'A',
      isCorrect: true,
      answeredAt: new Date()
    });

    // Simulate session recovery
    const recoveredSession = SessionManager.attemptRecovery();
    expect(recoveredSession).toBeDefined();
    expect(recoveredSession?.sessionId).toBe(originalSession.sessionId);

    // Simulate corrupted session data
    mockSessionStorage.getItem.mockReturnValue('invalid-json');
    const failedRecovery = SessionManager.attemptRecovery();
    expect(failedRecovery).toBeNull();
  });
});