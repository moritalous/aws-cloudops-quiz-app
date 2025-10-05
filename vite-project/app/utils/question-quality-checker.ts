import type { Question, QuestionSet } from '~/types';

export interface QualityIssue {
  questionId: string;
  severity: 'error' | 'warning' | 'info';
  category: 'content' | 'format' | 'consistency';
  message: string;
  suggestion?: string;
}

export interface QualityReport {
  overallScore: number; // 0-100
  totalIssues: number;
  issues: QualityIssue[];
  summary: {
    errors: number;
    warnings: number;
    info: number;
  };
}

/**
 * 問題の品質をチェックする
 */
export function checkQuestionQuality(question: Question): QualityIssue[] {
  const issues: QualityIssue[] = [];

  // 問題文の長さチェック
  if (question.question.length < 20) {
    issues.push({
      questionId: question.id,
      severity: 'warning',
      category: 'content',
      message: 'Question text is too short',
      suggestion: 'Consider adding more context or detail to the question'
    });
  }

  if (question.question.length > 500) {
    issues.push({
      questionId: question.id,
      severity: 'warning',
      category: 'content',
      message: 'Question text is very long',
      suggestion: 'Consider breaking down into smaller, more focused questions'
    });
  }

  // 選択肢の数チェック
  if (question.options.length < 3) {
    issues.push({
      questionId: question.id,
      severity: 'error',
      category: 'format',
      message: 'Too few answer options',
      suggestion: 'Add more plausible distractors'
    });
  }

  if (question.options.length > 5) {
    issues.push({
      questionId: question.id,
      severity: 'warning',
      category: 'format',
      message: 'Too many answer options',
      suggestion: 'Consider reducing to 4-5 options for better usability'
    });
  }

  // 選択肢の長さバランスチェック
  const optionLengths = question.options.map(opt => opt.length);
  const avgLength = optionLengths.reduce((a, b) => a + b, 0) / optionLengths.length;
  const hasImbalancedOptions = optionLengths.some(len => 
    Math.abs(len - avgLength) > avgLength * 0.5
  );

  if (hasImbalancedOptions) {
    issues.push({
      questionId: question.id,
      severity: 'info',
      category: 'format',
      message: 'Answer options have significantly different lengths',
      suggestion: 'Try to balance the length of answer options'
    });
  }

  // 解説の長さチェック
  if (question.explanation.length < 50) {
    issues.push({
      questionId: question.id,
      severity: 'warning',
      category: 'content',
      message: 'Explanation is too brief',
      suggestion: 'Provide more detailed explanation including why other options are incorrect'
    });
  }

  // 学習リソースの存在チェック
  if (question.learningResources.length === 0) {
    issues.push({
      questionId: question.id,
      severity: 'warning',
      category: 'content',
      message: 'No learning resources provided',
      suggestion: 'Add relevant AWS documentation links'
    });
  }

  // 関連サービスの存在チェック
  if (question.relatedServices.length === 0) {
    issues.push({
      questionId: question.id,
      severity: 'info',
      category: 'content',
      message: 'No related services specified',
      suggestion: 'Add relevant AWS services for better categorization'
    });
  }

  // タグの存在チェック
  if (question.tags.length === 0) {
    issues.push({
      questionId: question.id,
      severity: 'info',
      category: 'content',
      message: 'No tags specified',
      suggestion: 'Add relevant tags for better searchability'
    });
  }

  // 複数選択問題の正解数チェック
  if (question.type === 'multiple' && Array.isArray(question.correctAnswer)) {
    if (question.correctAnswer.length < 2) {
      issues.push({
        questionId: question.id,
        severity: 'error',
        category: 'consistency',
        message: 'Multiple choice question should have at least 2 correct answers',
        suggestion: 'Add more correct answers or change to single choice'
      });
    }

    if (question.correctAnswer.length >= question.options.length) {
      issues.push({
        questionId: question.id,
        severity: 'error',
        category: 'consistency',
        message: 'Too many correct answers for multiple choice question',
        suggestion: 'Reduce correct answers or add more options'
      });
    }
  }

  return issues;
}

/**
 * 問題セット全体の品質をチェックする
 */
export function checkQuestionSetQuality(questionSet: QuestionSet): QualityReport {
  const allIssues: QualityIssue[] = [];

  // 各問題の品質チェック
  for (const question of questionSet.questions) {
    const questionIssues = checkQuestionQuality(question);
    allIssues.push(...questionIssues);
  }

  // ドメイン分布チェック
  const domainCounts = Object.values(questionSet.domains);
  const totalQuestions = domainCounts.reduce((a, b) => a + b, 0);
  const minDomainPercentage = Math.min(...domainCounts) / totalQuestions * 100;
  const maxDomainPercentage = Math.max(...domainCounts) / totalQuestions * 100;

  if (maxDomainPercentage > 50) {
    allIssues.push({
      questionId: 'dataset',
      severity: 'warning',
      category: 'consistency',
      message: 'One domain dominates the question set',
      suggestion: 'Balance questions across all exam domains'
    });
  }

  if (minDomainPercentage < 5) {
    allIssues.push({
      questionId: 'dataset',
      severity: 'warning',
      category: 'consistency',
      message: 'Some domains have very few questions',
      suggestion: 'Add more questions to underrepresented domains'
    });
  }

  // 難易度分布チェック
  const difficultyCount = {
    easy: 0,
    medium: 0,
    hard: 0
  };

  for (const question of questionSet.questions) {
    difficultyCount[question.difficulty]++;
  }

  const easyPercentage = difficultyCount.easy / totalQuestions * 100;
  const hardPercentage = difficultyCount.hard / totalQuestions * 100;

  if (easyPercentage > 60) {
    allIssues.push({
      questionId: 'dataset',
      severity: 'info',
      category: 'consistency',
      message: 'Too many easy questions',
      suggestion: 'Add more medium and hard questions for better exam preparation'
    });
  }

  if (hardPercentage < 10) {
    allIssues.push({
      questionId: 'dataset',
      severity: 'info',
      category: 'consistency',
      message: 'Too few hard questions',
      suggestion: 'Add more challenging questions to better prepare for the exam'
    });
  }

  // 統計計算
  const summary = {
    errors: allIssues.filter(i => i.severity === 'error').length,
    warnings: allIssues.filter(i => i.severity === 'warning').length,
    info: allIssues.filter(i => i.severity === 'info').length
  };

  // スコア計算 (エラーは-10点、警告は-3点、情報は-1点)
  const maxScore = 100;
  const deductions = summary.errors * 10 + summary.warnings * 3 + summary.info * 1;
  const overallScore = Math.max(0, maxScore - deductions);

  return {
    overallScore,
    totalIssues: allIssues.length,
    issues: allIssues,
    summary
  };
}

/**
 * 品質レポートを人間が読みやすい形式で出力する
 */
export function formatQualityReport(report: QualityReport): string {
  const lines: string[] = [];
  
  lines.push(`Quality Report`);
  lines.push(`=============`);
  lines.push(`Overall Score: ${report.overallScore}/100`);
  lines.push(`Total Issues: ${report.totalIssues}`);
  lines.push(`- Errors: ${report.summary.errors}`);
  lines.push(`- Warnings: ${report.summary.warnings}`);
  lines.push(`- Info: ${report.summary.info}`);
  lines.push('');

  if (report.issues.length > 0) {
    lines.push('Issues:');
    lines.push('-------');
    
    for (const issue of report.issues) {
      const icon = issue.severity === 'error' ? '❌' : 
                   issue.severity === 'warning' ? '⚠️' : 'ℹ️';
      lines.push(`${icon} [${issue.questionId}] ${issue.message}`);
      if (issue.suggestion) {
        lines.push(`   💡 ${issue.suggestion}`);
      }
      lines.push('');
    }
  } else {
    lines.push('✅ No issues found!');
  }

  return lines.join('\n');
}