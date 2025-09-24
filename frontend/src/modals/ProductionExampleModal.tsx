// SPDX-License-Identifier: Apache-2.0
// src/modals/ProductionExampleModal.tsx
import { useState, useEffect } from "react";
import { createPortal } from "react-dom";

export default function ProductionExampleModal({
  open,
  onClose,
  text,
}: {
  open: boolean;
  onClose: () => void;
  text: string;
}) {
  const [mounted, setMounted] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => setMounted(true), []);
  useEffect(() => {
    if (!open) setCopied(false);
  }, [open]);

  if (!open || !mounted) return null;

  const copy = async () => {
    await navigator.clipboard.writeText(text || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  const Modal = (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4 sm:p-8 bg-black/50"
      aria-modal="true"
      role="dialog"
    >
      <div className="w-full max-w-[1000px] max-h-[85vh] bg-white rounded-2xl shadow-xl flex flex-col">
        {/* header */}
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h3 className="text-lg font-semibold">📝 광고 작업지시서 예시</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            닫기
          </button>
        </div>

        {/* body */}
        <div className="flex-1 overflow-auto p-5">
          <textarea
            className="w-full flex-1 min-h-[60vh] resize-y border rounded p-3 text-sm leading-6"
            defaultValue={text}
            readOnly
          />
        </div>

        {/* footer */}
        <div className="flex justify-end gap-2 px-5 py-4 border-t">
          <button
            onClick={copy}
            className="px-3 py-2 text-sm bg-indigo-600 text-white rounded disabled:opacity-60"
          >
            {copied ? "복사됨!" : "복사"}
          </button>
          <button onClick={onClose} className="px-3 py-2 text-sm border rounded">
            닫기
          </button>
        </div>
      </div>
    </div>
  );

  return createPortal(Modal, document.body);
}