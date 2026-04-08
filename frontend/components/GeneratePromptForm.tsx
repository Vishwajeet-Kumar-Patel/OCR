"use client";

import { useState } from "react";

type Props = {
  disabled?: boolean;
  disabledReason?: string;
  onGenerate: (payload: {
    product_name: string;
    product_benefit: string;
    cta_text: string;
    target_audience: string;
  }) => Promise<void>;
  finalPrompt: string;
};

export default function GeneratePromptForm({ disabled, disabledReason, onGenerate, finalPrompt }: Props) {
  const [form, setForm] = useState({
    product_name: "",
    product_benefit: "",
    cta_text: "",
    target_audience: ""
  });

  return (
    <section className="rounded-2xl bg-white/90 p-6 shadow-card">
      <h2 className="mb-3 text-2xl font-semibold">4) Generate Prompt for New Product</h2>
      <div className="grid gap-3 md:grid-cols-2">
        {[
          ["product_name", "Product name"],
          ["product_benefit", "Product benefit"],
          ["cta_text", "CTA text"],
          ["target_audience", "Target audience"]
        ].map(([key, label]) => (
          <input
            key={key}
            className="rounded-lg border border-slate-300 px-3 py-2"
            placeholder={label}
            value={form[key as keyof typeof form]}
            onChange={(e) => setForm((prev) => ({ ...prev, [key]: e.target.value }))}
          />
        ))}
      </div>
      <button
        disabled={disabled}
        onClick={() => onGenerate(form)}
        className="mt-4 rounded-lg bg-ink px-5 py-2 font-semibold text-white disabled:opacity-50"
      >
        Generate Final Prompt
      </button>
      {disabled ? <p className="mt-2 text-xs text-slate-500">{disabledReason ?? "Complete earlier steps first."}</p> : null}

      {finalPrompt ? (
        <div className="mt-4 rounded-xl bg-warm/40 p-4">
          <h3 className="font-semibold">Final Prompt</h3>
          <pre className="mt-2 whitespace-pre-wrap text-sm">{finalPrompt}</pre>
        </div>
      ) : null}
    </section>
  );
}
