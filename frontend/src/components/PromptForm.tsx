import React from 'react';

interface PromptFormProps {
  prompt: string;
  setPrompt: React.Dispatch<React.SetStateAction<string>>;
  onSubmit: (input: string) => Promise<void>;
  loading: boolean;
}

const PromptForm: React.FC<PromptFormProps> = ({ prompt, setPrompt, onSubmit, loading }) => {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(prompt);
      }}
      className="space-y-4"
    >
      <textarea
        placeholder="예: 학생들을 대상으로 한 노트북 할인 판매 플렛폼 광고를 만들거야. 분위기는 희망차고 리드미컬하게."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={5}
        className="w-full border border-gray-300 rounded-lg p-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md font-semibold hover:bg-blue-700 transition"
      >
        {loading ? '⏳ 생성 중...' : '🎯 광고 요소 추출'}
      </button>
    </form>
  );
};

export default PromptForm;