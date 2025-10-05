import type { Route } from "./+types/result";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "結果 - AWS CloudOps試験対策" },
    { name: "description", content: "クイズの結果と統計" },
  ];
}

export default function Result() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          クイズ結果
        </h1>
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-gray-600">結果表示機能は実装中です...</p>
        </div>
      </div>
    </div>
  );
}