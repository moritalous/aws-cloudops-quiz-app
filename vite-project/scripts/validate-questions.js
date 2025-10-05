#!/usr/bin/env node

/**
 * 問題データの検証スクリプト
 * 使用方法: node scripts/validate-questions.js
 */

import { readFileSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 簡易版のスキーマ検証（Node.js環境用）
function validateQuestionData(data) {
  const errors = [];

  // 基本構造チェック
  if (!data.version) errors.push('Missing version');
  if (!data.generatedAt) errors.push('Missing generatedAt');
  if (!data.totalQuestions) errors.push('Missing totalQuestions');
  if (!data.domains) errors.push('Missing domains');
  if (!Array.isArray(data.questions)) errors.push('Questions must be an array');

  // 問題数の整合性チェック
  if (data.questions && data.questions.length !== data.totalQuestions) {
    errors.push(`Question count mismatch: expected ${data.totalQuestions}, got ${data.questions.length}`);
  }

  // 各問題の基本チェック
  if (data.questions) {
    data.questions.forEach((question, index) => {
      if (!question.id) errors.push(`Question ${index}: Missing id`);
      if (!question.question) errors.push(`Question ${index}: Missing question text`);
      if (!Array.isArray(question.options)) errors.push(`Question ${index}: Options must be an array`);
      if (!question.correctAnswer) errors.push(`Question ${index}: Missing correctAnswer`);
      if (!question.explanation) errors.push(`Question ${index}: Missing explanation`);
    });
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

function checkQuality(data) {
  const issues = [];

  if (data.questions) {
    data.questions.forEach(question => {
      // 問題文の長さチェック
      if (question.question && question.question.length < 20) {
        issues.push(`${question.id}: Question text is too short`);
      }

      // 選択肢の数チェック
      if (question.options && question.options.length < 3) {
        issues.push(`${question.id}: Too few answer options`);
      }

      // 解説の長さチェック
      if (question.explanation && question.explanation.length < 30) {
        issues.push(`${question.id}: Explanation is too brief`);
      }

      // 学習リソースチェック
      if (!question.learningResources || question.learningResources.length === 0) {
        issues.push(`${question.id}: No learning resources provided`);
      }
    });
  }

  return issues;
}

try {
  console.log('🔍 Validating questions.json...\n');

  // ファイル読み込み
  const questionsPath = join(__dirname, '../public/questions.json');
  const questionsData = JSON.parse(readFileSync(questionsPath, 'utf8'));

  // スキーマ検証
  console.log('📋 Schema Validation:');
  const validation = validateQuestionData(questionsData);
  
  if (validation.isValid) {
    console.log('✅ Schema validation passed');
  } else {
    console.log('❌ Schema validation failed:');
    validation.errors.forEach(error => console.log(`   - ${error}`));
  }

  console.log('');

  // 品質チェック
  console.log('🎯 Quality Check:');
  const qualityIssues = checkQuality(questionsData);
  
  if (qualityIssues.length === 0) {
    console.log('✅ No quality issues found');
  } else {
    console.log(`⚠️  Found ${qualityIssues.length} quality issues:`);
    qualityIssues.forEach(issue => console.log(`   - ${issue}`));
  }

  console.log('');

  // 統計情報
  console.log('📊 Statistics:');
  console.log(`   Total Questions: ${questionsData.totalQuestions}`);
  console.log(`   Domains: ${Object.keys(questionsData.domains).join(', ')}`);
  
  if (questionsData.questions) {
    const difficulties = questionsData.questions.reduce((acc, q) => {
      acc[q.difficulty] = (acc[q.difficulty] || 0) + 1;
      return acc;
    }, {});
    
    console.log(`   Difficulty Distribution:`);
    Object.entries(difficulties).forEach(([diff, count]) => {
      console.log(`     ${diff}: ${count}`);
    });
  }

  console.log('\n✨ Validation complete!');

} catch (error) {
  console.error('❌ Error during validation:', error.message);
  process.exit(1);
}