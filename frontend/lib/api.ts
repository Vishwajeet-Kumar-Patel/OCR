import axios from "axios";
import type { AdAnalysis, FinalPromptRequest, PatternReport, TemplateResult } from "./types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  timeout: 120000
});

export async function uploadAds(files: File[]): Promise<{ job_id: string; image_count: number }> {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));

  const { data } = await api.post("/ads/upload", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
}

export async function analyzeAds(jobId: string): Promise<{ analyses: AdAnalysis[] }> {
  const { data } = await api.post("/ads/analyze", { job_id: jobId });
  return data;
}

export async function extractPatterns(jobId: string): Promise<PatternReport> {
  const { data } = await api.post("/ads/patterns", { job_id: jobId });
  return data;
}

export async function buildTemplate(jobId: string): Promise<TemplateResult> {
  const { data } = await api.post("/prompt/template", { job_id: jobId });
  return data;
}

export async function generatePrompt(payload: { job_id: string; inputs: FinalPromptRequest }) {
  const { data } = await api.post("/prompt/generate", payload);
  return data as { prompt: string };
}
