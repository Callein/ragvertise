// SPDX-License-Identifier: Apache-2.0
import { useState } from 'react';
import PromptForm from '@/components/PromptForm';
import ResultModal from '@/modals/ResponseModal';
import { extractAdElements } from '@/services/api';

export default function Home() {
  // 타입 명시: extractAdElements 반환 타입 또는 null
  const [result, setResult] = useState<Awaited<ReturnType<typeof extractAdElements>> | null>(null);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [prompt, setPrompt] = useState('');

  const handleSubmit = async (input: string) => {
    setPrompt(input);
    setLoading(true);
    try {
      const res = await extractAdElements(input);
      setResult(res);
      setIsModalOpen(true);
    } catch {
      alert('API 요청 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    handleSubmit(prompt);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 via-white to-gray-200 flex items-center justify-center px-4 py-8">
      <div className="bg-white p-8 md:p-10 rounded-2xl shadow-2xl w-full max-w-2xl transition-all">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">🧠 Ragvertise 프롬프트 테스트</h1>
        <p className="text-center text-gray-500 mb-6 text-sm">
          원하는 광고의 설명을 입력하면 AI가 광고 요소를 분석 후 포트폴리오를 추천해드립니다.
        </p>
        <PromptForm
          onSubmit={handleSubmit}
          loading={loading}
          prompt={prompt}
          setPrompt={setPrompt}
        />
        <ResultModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onRetry={handleRetry}
          result={result}
        />
      </div>
    </div>
  );
}