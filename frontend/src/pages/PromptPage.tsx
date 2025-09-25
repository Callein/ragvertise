// SPDX-License-Identifier: Apache-2.0
import { useState } from "react";
import { extractAdElements } from "@/services/api";
import PromptForm from "../components/PromptForm";
import ResponseModal from "../modals/ResponseModal";

export default function PromptPage() {
  const [prompt, setPrompt] = useState("");
  // 타입 명시: extractAdElements 반환 타입 또는 null
  const [response, setResponse] = useState<Awaited<ReturnType<typeof extractAdElements>> | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const result = await extractAdElements(prompt);
      setResponse(result);
      setIsModalOpen(true);
    } catch (error) {
      console.error("API 요청 실패:", error);
      alert("API 요청에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    handleSubmit();
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <PromptForm
        prompt={prompt}
        setPrompt={setPrompt}
        onSubmit={handleSubmit}
        loading={loading}
      />

      {isModalOpen && response && (
        <ResponseModal
          isOpen={isModalOpen}
          result={response}
          onClose={() => setIsModalOpen(false)}
          onRetry={handleRetry}
        />
      )}
    </div>
  );
}