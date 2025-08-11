import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
});

// 요소 추출 (v3 경로 권장)
export async function extractAdElements(userPrompt: string) {
  const { data } = await http.post("/api/v3/ad-element/extract", {
    user_prompt: userPrompt,
  });
  return data;
}

export interface AdElementsRequest {
  desc: string;
  what: string;
  how: string;
  style: string;
  diversity?: boolean;
  limit?: number; // 선택적
}

// === v3 응답 타입 ===
export interface SearchResultV3 {
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

  // 새 메타
  view_lnk_url?: string | null;
  prdn_stdo_nm?: string | null;
  prdn_cost?: number | null;
  prdn_perd?: string | null;
}

export interface RankResponseV3 {
  generated: { desc: string; what: string; how: string; style: string };
  search_results: SearchResultV3[];
  top_studios: { name: string; count: number; ratio: number }[]; // NEW
  candidate_size: number; // NEW
}

export async function getRankedPortfoliosByAdElements(payload: AdElementsRequest) {
  const { data } = await http.post<RankResponseV3>(
    "/api/v3/rank/portfolios/by-ad-elements",
    payload
  );
  return data;
}