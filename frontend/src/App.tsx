import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-xl mx-auto bg-white rounded-xl shadow-md p-6">
        <h1 className="text-2xl font-bold mb-4 text-gray-800">🔍 API 테스트</h1>

        <div className="mb-4">
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-1">
            프롬프트 입력
          </label>
          <textarea
            id="prompt"
            className="w-full border border-gray-300 rounded-md p-2"
            rows={4}
            placeholder="예: 중장년 여성을 위한 따뜻한 유산균 광고를 만들고 싶어요."
          ></textarea>
        </div>

        <button
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition"
        >
          🔎 검색
        </button>
      </div>
    </div>
  );
}

export default App;