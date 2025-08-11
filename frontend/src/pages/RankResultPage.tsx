import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  getRankedPortfoliosByAdElements,
  AdElementsRequest,
  RankResponseV3,
  SearchResultV3,
} from "@/services/api";

export default function RankResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as AdElementsRequest | null;

  const [data, setData] = useState<RankResponseV3 | null>(null);
  const [loading, setLoading] = useState(false);
  const [showFormula, setShowFormula] = useState(false);

  useEffect(() => {
    if (!state) {
      navigate("/");
      return;
    }
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await getRankedPortfoliosByAdElements({
          ...state,
          diversity: state.diversity ?? false,
          // limit: state.limit ?? 5, // 필요 시 사용
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

  if (loading) return <div className="p-4 text-gray-600">불러오는 중…</div>;
  if (!data) return <div className="p-4 text-red-500">데이터 없음</div>;

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-10">
      <div className="flex justify-between items-center">
        <button
          onClick={() => setShowFormula(!showFormula)}
          className="text-sm text-blue-600 hover:underline"
        >
          📊 점수 산정 방식 및 요소 설명 보기
        </button>
        <button onClick={() => navigate("/")} className="text-sm text-blue-600 hover:underline">
          ⬅ 홈으로 돌아가기
        </button>
      </div>

      {showFormula && <ScoreFormulaNotice />}

      <AdElementsSection data={data.generated} />

      <TopStudiosSection
        studios={data.top_studios}
        candidateSize={data.candidate_size}
      />

      <PortfolioList results={data.search_results} />
    </div>
  );
}

function AdElementsSection({ data }: { data: RankResponseV3["generated"] }) {
  return (
    <section>
      <h2 className="text-2xl font-bold mb-4">🧠 생성된 광고 요소</h2>
      <ul className="bg-white p-4 border rounded-lg space-y-2 text-gray-700 shadow-sm">
        <li><strong>Desc:</strong> {data.desc}</li>
        <li><strong>What:</strong> {data.what}</li>
        <li><strong>How:</strong> {data.how}</li>
        <li><strong>Style:</strong> {data.style}</li>
      </ul>
    </section>
  );
}

function TopStudiosSection({
  studios,
  candidateSize,
}: {
  studios: RankResponseV3["top_studios"];
  candidateSize: number;
}) {
  if (!studios?.length) return null;
  return (
    <section>
      <h2 className="text-2xl font-bold mb-2">🏆 상위 스튜디오</h2>
      <p className="text-sm text-gray-500 mb-3">
        후보 {candidateSize}개 중 가장 많이 노출된 스튜디오 TOP {studios.length}
      </p>
      <div className="grid sm:grid-cols-3 gap-3">
        {studios.map((s) => (
          <div key={s.name} className="bg-white border rounded-lg p-4 shadow-sm">
            <div className="text-lg font-semibold truncate" title={s.name}>{s.name}</div>
            <div className="text-gray-600 text-sm mt-1">
              {s.count}회 ({(s.ratio * 100).toFixed(1)}%)
            </div>
          </div>
        ))}
      </div>
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
      <div className="overflow-x-auto mt-2">
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
              <td className="px-4 py-2 border-b">desc/what/how/style을 하나로 합친 전체 문장</td>
              <td className="px-4 py-2 border-b">SBERT → 코사인 유사도</td>
            </tr>
            <tr>
              <td className="px-4 py-2 border-b font-medium">desc</td>
              <td className="px-4 py-2 border-b">요청 광고의 한 문장 요약</td>
              <td className="px-4 py-2 border-b">SBERT → 코사인 유사도</td>
            </tr>
            <tr>
              <td className="px-4 py-2 border-b font-medium">what</td>
              <td className="px-4 py-2 border-b">무엇을 광고하는지(중분류, 한 단어)</td>
              <td className="px-4 py-2 border-b">fastText 평균 → 코사인</td>
            </tr>
            <tr>
              <td className="px-4 py-2 border-b font-medium">how</td>
              <td className="px-4 py-2 border-b">어떤 방식/매체/도구로 광고하는지</td>
              <td className="px-4 py-2 border-b">SBERT → 코사인 유사도</td>
            </tr>
            <tr>
              <td className="px-4 py-2 font-medium">style</td>
              <td className="px-4 py-2">광고의 톤/연출 스타일(한 단어)</td>
              <td className="px-4 py-2">SBERT → 코사인 유사도</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}

function PortfolioList({ results }: { results: SearchResultV3[] }) {
  return (
    <section>
      <h2 className="text-2xl font-bold mb-4">📈 추천 포트폴리오 (Top {results.length})</h2>
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

            <div className="flex items-center gap-3 flex-wrap">
              <h3 className="text-lg font-semibold text-gray-800">{ptfo.ptfo_nm}</h3>
              {ptfo.prdn_stdo_nm && (
                <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-1 rounded-full">
                  {ptfo.prdn_stdo_nm}
                </span>
              )}
              {ptfo.view_lnk_url && (
                <a
                  href={ptfo.view_lnk_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-blue-600 hover:underline"
                >
                  ▶ 영상 보기
                </a>
              )}
            </div>

            <p className="text-gray-700 mt-1">{ptfo.ptfo_desc}</p>

            {(ptfo.prdn_cost || ptfo.prdn_perd) && (
              <div className="text-sm text-gray-600 mt-1">
                {ptfo.prdn_cost && <>제작비: {ptfo.prdn_cost.toLocaleString()} </>}
                {ptfo.prdn_perd && <span className="ml-2">제작기간: {ptfo.prdn_perd}</span>}
              </div>
            )}

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