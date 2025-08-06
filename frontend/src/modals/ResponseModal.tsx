import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {NavigateFunction, useNavigate} from "react-router-dom";

interface ResponseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRetry: () => void;
  result: {
    desc: string;
    what: string;
    how: string;
    style: string;
  } | null;
}

const ResponseModal: React.FC<ResponseModalProps> = ({ isOpen, onClose, onRetry, result }) => {
  const navigate: NavigateFunction = useNavigate();

  const handleNavigate = () => {
    if (!result) return;
    navigate("/rank-result", { state: result });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <div className="w-[450px] mx-auto">
          <DialogHeader>
            <DialogTitle>🎯 광고 요소 결과</DialogTitle>
          </DialogHeader>

          <div className="space-y-2 text-sm">
            <p><strong>Desc:</strong> {result?.desc}</p>
            <p><strong>What:</strong> {result?.what}</p>
            <p><strong>How:</strong> {result?.how}</p>
            <p><strong>Style:</strong> {result?.style}</p>
          </div>

          <div className="mt-6 flex justify-between gap-2">
            <Button
                onClick={onRetry}
                className="bg-gray-200 text-gray-600 hover:bg-gray-300"
            >
              다시 요청
            </Button>
            <Button
                onClick={handleNavigate}
                className="bg-blue-600 text-white hover:bg-blue-700"
            >
              포트폴리오 추천 받기
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ResponseModal;