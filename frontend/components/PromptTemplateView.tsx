import type { PatternReport, TemplateResult } from "@/lib/types";

type Props = {
  report: PatternReport | null;
  template: TemplateResult | null;
};

export default function PromptTemplateView({ report, template }: Props) {
  if (!report && !template) return null;

  return (
    <section className="rounded-2xl bg-white/90 p-6 shadow-card">
      <h2 className="mb-3 text-2xl font-semibold">3) Patterns + Reusable Template</h2>

      {report ? (
        <div className="mb-6 rounded-xl border border-slate-200 p-4">
          <h3 className="font-semibold">Pattern Insight Report</h3>
          <p className="mt-2 text-sm text-slate-700">{report.summary}</p>
          <pre className="mt-3 overflow-auto rounded bg-slate-50 p-3 text-xs">{JSON.stringify(report, null, 2)}</pre>
        </div>
      ) : null}

      {template ? (
        <div className="rounded-xl border border-accent/30 bg-accent/5 p-4">
          <h3 className="font-semibold">Prompt Template</h3>
          <pre className="mt-2 whitespace-pre-wrap text-sm">{template.template}</pre>
          <p className="mt-2 text-xs text-slate-600">Variables: {template.variables.join(", ")}</p>
        </div>
      ) : null}
    </section>
  );
}
