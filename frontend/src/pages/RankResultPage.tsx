import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getRankedPortfoliosByAdElements, AdElementsRequest } from "@/services/api";

interface SearchResult {
  ptfo_seqno: number;
  ptfo_nm: string;
  ptfo_desc: string;
  final_score: number;
  desc: string;
  desc_score: number;
  what: string;
  what_score: number;
  how: string;
  how_score: number;
  style: string;
  style_score: number;
  tags: string[];
}

interface RankResponse {
  generated: {
    desc: string;
    what: string;
    how: string;
    style: string;
  };
  search_results: SearchResult[];
}

export default function RankResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as AdElementsRequest | null;

  const [data, setData] = useState<RankResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [showFormula, setShowFormula] = useState(false);

  useEffect(() => {
    if (!state) {
      // 직접 접근 시 Home으로 보냄
      navigate("/");
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await getRankedPortfoliosByAdElements({
          ...state,
          diversity: false,
        });
        setData(res);
      } catch (err) {
        console.error("API Error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [state, navigate]);

  if (loading) return <div className="p-4 text-gray-600">불러오는 중...(약 10초 소요)</div>;
  if (!data) return <div className="p-4 text-red-500">데이터 없음</div>;

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-10">
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <button
            onClick={() => setShowFormula(!showFormula)}
            className="text-sm text-blue-600 hover:underline"
          >
            📊 점수 산정 방식 및 요소 설명 보기
          </button>
        </div>
        <button
          onClick={() => navigate("/")}
          className="text-sm text-blue-600 hover:underline"
        >
          ⬅ 홈으로 돌아가기
        </button>
      </div>
      {showFormula && <ScoreFormulaNotice />}

      <AdElementsSection data={data.generated} />

      <PortfolioList results={data.search_results} />
    </div>
  );
}

function AdElementsSection({ data }: { data: RankResponse["generated"] }) {
  return (
    <section>
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">🧠 생성된 광고 요소</h2>
      <ul className="bg-white p-4 border rounded-lg space-y-2 text-gray-700 shadow-sm">
        <li><strong>Desc:</strong> {data.desc}</li>
        <li><strong>What:</strong> {data.what}</li>
        <li><strong>How:</strong> {data.how}</li>
        <li><strong>Style:</strong> {data.style}</li>
      </ul>
    </section>
  );
}

function ScoreFormulaNotice() {
  return (
      <section className="bg-yellow-50 border-l-4 border-yellow-400 p-4 text-sm text-gray-800 rounded space-y-4">
        <p className="font-semibold mb-1">📊 점수 산정 방식</p>
        <p>최종 점수는 다음 요소별 유사도에 아래 가중치를 곱해 합산하여 계산됩니다:</p>
        <pre className="mt-2 text-gray-700 font-mono text-sm bg-white p-2 rounded overflow-x-auto">
      {`final_score = 
        full_score × 1.0 + 
        desc_score × 0.6 + 
        what_score × 1.5 + 
        how_score × 0.2 + 
        style_score × 0.5`}
      </pre>

        <p className="font-semibold mb-1">🎯 요소 설명</p>

        <div className="overflow-x-auto mt-4">
          <table className="table-auto w-full text-left text-sm border border-gray-200 bg-white">
            <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-4 py-2 border-b">요소</th>
              <th className="px-4 py-2 border-b">설명</th>
              <th className="px-4 py-2 border-b">유사도 방식</th>
            </tr>
            </thead>
            <tbody>
            <tr>
              <td className="px-4 py-2 border-b font-medium">full</td>
              <td className="px-4 py-2 border-b">광고 요소(desc, what, how, style)를 하나의 문장으로 결합한 전체 텍스트</td>
              <td className="px-4 py-2 border-b">SBERT → 코사인 유사도</td>
            </tr>
            <tr>
              <td className="px-4 py-2 border-b font-medium">desc</td>
              <td className="px-4 py-2 border-b">사용자가 요청한 광고의 내용을 한 문장으로 요약한 항목</td>
              <td className="px-4 py-2 border-b">SBERT → 코사인 유사도</td>
            </tr>
            <tr>
              <td className="px-4 py-2 border-b font-medium">what</td>
              <td className="px-4 py-2 border-b">무엇을 광고하는지 중분류 수준에서 한 단어로 표현한 항목</td>
              <td className="px-4 py-2 border-b">fastText → 단어 평균 → 코사인 유사도</td>
            </tr>
            <tr>
              <td className="px-4 py-2 border-b font-medium">how</td>
              <td className="px-4 py-2 border-b">어떤 방식, 매체, 수단으로 광고가 전달되는지를 한 단어로 표현한 항목</td>
              <td className="px-4 py-2 border-b">SBERT → 코사인 유사도</td>
            </tr>
            <tr>
              <td className="px-4 py-2 font-medium">style</td>
              <td className="px-4 py-2">광고의 연출 방식이나 분위기를 한 단어로 표현한 항목</td>
              <td className="px-4 py-2">SBERT → 코사인 유사도</td>
            </tr>
            </tbody>
          </table>
        </div>
      </section>
  );
}


function PortfolioList({results}: { results: SearchResult[] }) {
  return (
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">📈 추천 포트폴리오 (Top {results.length})</h2>
        <div className="space-y-6">
          {results.map((ptfo, idx) => (
              <div
                  key={ptfo.ptfo_seqno}
                  className="border border-gray-200 p-4 rounded-lg shadow-sm bg-white"
              >
                <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                  <span># {idx + 1}</span>
                  <span>Score: {ptfo.final_score.toFixed(2)}</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-800">{ptfo.ptfo_nm}</h3>
                <p className="text-gray-700 mt-1">{ptfo.ptfo_desc}</p>
                <table className="table-auto w-full text-sm text-left mt-4 border border-gray-200">
                  <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 border-b">요소</th>
                    <th className="px-4 py-2 border-b">값</th>
                    <th className="px-4 py-2 border-b">점수</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="px-4 py-2 border-b">Desc</td>
                  <td className="px-4 py-2 border-b">{ptfo.desc}</td>
                  <td className="px-4 py-2 border-b">{ptfo.desc_score.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 border-b">What</td>
                  <td className="px-4 py-2 border-b">{ptfo.what}</td>
                  <td className="px-4 py-2 border-b">{ptfo.what_score.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 border-b">How</td>
                  <td className="px-4 py-2 border-b">{ptfo.how}</td>
                  <td className="px-4 py-2 border-b">{ptfo.how_score.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="px-4 py-2">Style</td>
                  <td className="px-4 py-2">{ptfo.style}</td>
                  <td className="px-4 py-2">{ptfo.style_score.toFixed(2)}</td>
                </tr>
              </tbody>
            </table>
            <div className="mt-2 flex flex-wrap gap-2">
              {ptfo.tags.map((tag) => (
                <span
                  key={tag}
                  className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}