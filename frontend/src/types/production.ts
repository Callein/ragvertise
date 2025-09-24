// SPDX-License-Identifier: Apache-2.0
export type Tag = string;

export interface Generated {
  desc: string;
  what: string;
  how: string;
  style: string;
}

export interface StudioStat {
  name: string;
  count: number;
  ratio: number; // 0~1
}

/**
 * 백엔드 V3 SearchResponse와 1:1 매핑
 */
export interface SearchResultV3 {
  final_score: number;

  full_score: number;
  desc_score: number;
  what_score: number;
  how_score: number;
  style_score: number;

  desc: string;
  what: string;
  how: string;
  style: string;

  ptfo_seqno: number;
  ptfo_nm: string;
  ptfo_desc: string;
  tags: Tag[];

  // 메타(옵셔널)
  view_lnk_url?: string | null;
  prdn_stdo_nm?: string | null;
  prdn_cost?: number | null;
  prdn_perd?: string | null;
}

export interface RankResponseV3 {
  generated: Generated;
  search_results: SearchResultV3[];
  top_studios: StudioStat[];
  candidate_size: number;
}

/** 작업지시서 생성 요청/응답 */
export interface ProductionExampleRequest {
  generated: Generated;
  search_results: SearchResultV3[];
  top_studios: StudioStat[];
  candidate_size: number;
}

export interface ProductionExampleResponse {
  example: string;
}

export interface TopStudioStat {
  name: string;
  count: number;
  ratio: number;
}