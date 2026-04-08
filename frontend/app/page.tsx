"use client";

import { useState } from "react";
import AdUploader from "@/components/AdUploader";
import AdAnalysisView from "@/components/AdAnalysisView";
import GeneratePromptForm from "@/components/GeneratePromptForm";
import PromptTemplateView from "@/components/PromptTemplateView";
import { analyzeAds, buildTemplate, extractPatterns, generatePrompt, uploadAds } from "@/lib/api";
import type { AdAnalysis, PatternReport, TemplateResult } from "@/lib/types";

export default function Home() {
  const [jobId, setJobId] = useState<string>("");
  const [loadingUpload, setLoadingUpload] = useState(false);
  const [loadingAnalyze, setLoadingAnalyze] = useState(false);
  const [analyses, setAnalyses] = useState<AdAnalysis[]>([]);
  const [report, setReport] = useState<PatternReport | null>(null);
  const [template, setTemplate] = useState<TemplateResult | null>(null);
  const [finalPrompt, setFinalPrompt] = useState("");
  const [error, setError] = useState("");

  const handleUpload = async (files: File[]) => {
    try {
      setError("");
      setLoadingUpload(true);
      const uploadRes = await uploadAds(files);
      setJobId(uploadRes.job_id);

      setLoadingAnalyze(true);
      const analysisRes = await analyzeAds(uploadRes.job_id);
      setAnalyses(analysisRes.analyses);

      const patternRes = await extractPatterns(uploadRes.job_id);
      setReport(patternRes);

      const templateRes = await buildTemplate(uploadRes.job_id);
      setTemplate(templateRes);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Pipeline failed. Please retry.");
    } finally {
      setLoadingUpload(false);
      setLoadingAnalyze(false);
    }
  };

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-10 md:px-8">
      <header>
        <h1 className="text-4xl font-black tracking-tight">Ad Prompt Intelligence Studio</h1>
        <p className="mt-2 max-w-2xl text-slate-700">
          Upload static ad images, extract OCR + visual patterns, build RAG insights, and generate reusable prompts for new products.
        </p>
      </header>

      {error ? <p className="rounded bg-red-100 px-3 py-2 text-sm text-red-800">{error}</p> : null}

      <AdUploader onUpload={handleUpload} loading={loadingUpload || loadingAnalyze} />
      <AdAnalysisView analyses={analyses} />
      <PromptTemplateView report={report} template={template} />
      <GeneratePromptForm
        disabled={!jobId || !template}
        disabledReason={!jobId ? "Upload and analyze ad images first." : "Generate a prompt template first."}
        onGenerate={async (inputs) => {
          const result = await generatePrompt({ job_id: jobId, inputs });
          setFinalPrompt(result.prompt);
        }}
        finalPrompt={finalPrompt}
      />
    </main>
  );
}
