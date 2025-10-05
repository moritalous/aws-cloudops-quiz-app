/**
 * SessionManager Demo Script
 * 
 * This script demonstrates the SessionManager functionality
 * Run this in a browser console to see the session management in action
 */

import { SessionManager } from '../session-manager';
import type { Answer } from '~/types';

export function demonstrateSessionManager() {
  console.log('=== SessionManager Demo ===\n');

  // 1. Create a new session
  console.log('1. Creating a new 10-question set session...');
  const session = SessionManager.createSession('set', 10, 'monitoring');
  console.log('Created session:', {
    id: session.sessionId,
    mode: session.mode,
    targetCount: session.targetQuestionCount,
    domainFilter: session.domainFilter
  });

  // 2. Add some answers
  console.log('\n2. Adding sample answers...');
  const sampleAnswers: Answer[] = [
    {
      questionId: 'q001',
      userAnswer: 'A',
      correctAnswer: 'A',
      isCorrect: true,
      answeredAt: new Date(),
      timeSpent: 30
    },
    {
      questionId: 'q002',
      userAnswer: 'B',
      correctAnswer: 'A',
      isCorrect: false,
      answeredAt: new Date(),
      timeSpent: 45
    },
    {
      questionId: 'q003',
      userAnswer: 'C',
      correctAnswer: 'C',
      isCorrect: true,
      answeredAt: new Date(),
      timeSpent: 25
    }
  ];

  sampleAnswers.forEach((answer, index) => {
    SessionManager.addAnswer(answer);
    console.log(`Added answer ${index + 1}:`, {
      questionId: answer.questionId,
      isCorrect: answer.isCorrect,
      timeSpent: answer.timeSpent
    });
  });

  // 3. Get current session and calculate statistics
  console.log('\n3. Current session statistics...');
  const currentSession = SessionManager.getSession();
  if (currentSession) {
    const stats = SessionManager.calculateStatistics(currentSession);
    console.log('Statistics:', {
      totalQuestions: stats.totalQuestions,
      correctAnswers: stats.correctAnswers,
      accuracy: `${stats.accuracy.toFixed(1)}%`,
      averageTime: stats.averageTimePerQuestion ? `${stats.averageTimePerQuestion.toFixed(1)}s` : 'N/A'
    });

    // 4. Get progress information
    const progress = SessionManager.getProgress(currentSession);
    console.log('Progress:', {
      current: progress.current,
      total: progress.total,
      percentage: progress.percentage ? `${progress.percentage}%` : 'N/A',
      isComplete: progress.isComplete
    });

    // 5. Get session duration
    const duration = SessionManager.getSessionDuration(currentSession);
    console.log('Session duration:', `${duration} seconds`);
  }

  // 6. Demonstrate domain statistics calculation
  console.log('\n4. Domain statistics (with mock question data)...');
  const questionMap = new Map([
    ['q001', { domain: 'monitoring' }],
    ['q002', { domain: 'security' }],
    ['q003', { domain: 'monitoring' }]
  ]);

  if (currentSession) {
    const domainStats = SessionManager.calculateDomainStatistics(currentSession, questionMap);
    console.log('Domain breakdown:', domainStats.domainBreakdown);
  }

  // 7. Demonstrate session validation
  console.log('\n5. Session validation...');
  if (currentSession) {
    const isValid = SessionManager.validateSession(currentSession);
    console.log('Session is valid:', isValid);
  }

  // 8. Demonstrate session recovery
  console.log('\n6. Session recovery test...');
  const recoveredSession = SessionManager.attemptRecovery();
  console.log('Recovered session:', recoveredSession ? 'Success' : 'Failed');

  // 9. Save session history (simulate completion)
  console.log('\n7. Saving session history...');
  if (currentSession) {
    SessionManager.saveSessionHistory(currentSession);
    const history = SessionManager.getSessionHistory();
    console.log('Session history entries:', history.length);
  }

  console.log('\n=== Demo Complete ===');
  console.log('Check sessionStorage and localStorage in DevTools to see stored data');
  
  return {
    session: currentSession,
    stats: currentSession ? SessionManager.calculateStatistics(currentSession) : null,
    progress: currentSession ? SessionManager.getProgress(currentSession) : null
  };
}

// Export for use in browser console
if (typeof window !== 'undefined') {
  (window as any).demonstrateSessionManager = demonstrateSessionManager;
}