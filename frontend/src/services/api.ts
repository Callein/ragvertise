import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function extractAdElements(userPrompt: string) {
  const res = await fetch(`${API_BASE_URL}/api/v2/ad-element/extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_prompt: userPrompt }),
  });
  if (!res.ok) throw new Error("Failed to extract ad elements");
  return res.json();
}

export interface AdElementsRequest {
  desc: string;
  what: string;
  how: string;
  style: string;
  diversity?: boolean;
}

export async function getRankedPortfoliosByAdElements(payload: AdElementsRequest) {
  const response = await axios.post(`${API_BASE_URL}/api/v2/rank/portfolios/by-ad-elements`, payload);
  return response.data;
}