import axios from "axios";
import type {
  RankResponseV3,
  SearchResultV3,
  ProductionExampleRequest,
  ProductionExampleResponse,
} from "@/types/production";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
});

// 요소 추출 (v3)
export async function extractAdElements(userPrompt: string) {
  const { data } = await http.post<{ desc: string; what: string; how: string; style: string }>(
    "/api/v3/ad-element/extract",
    { user_prompt: userPrompt }
  );
  return data;
}

export interface AdElementsRequest {
  desc: string;
  what: string;
  how: string;
  style: string;
  diversity?: boolean;
  limit?: number;
}

// V3 랭킹
export async function getRankedPortfoliosByAdElements(
  payload: AdElementsRequest
): Promise<RankResponseV3> {
  const { data } = await http.post<RankResponseV3>(
    "/api/v3/rank/portfolios/by-ad-elements",
    payload
  );
  return data;
}

// 작업지시서 예시 생성
export async function createProductionExample(
  payload: ProductionExampleRequest
): Promise<ProductionExampleResponse> {
  const { data } = await http.post<ProductionExampleResponse>(
    "/api/v3/production_example/generate",
    payload
  );
  return data;
}

export type {
  RankResponseV3,
  SearchResultV3,
  ProductionExampleRequest,
  ProductionExampleResponse,
};