import type { AdAnalysis } from "@/lib/types";

type Props = {
  analyses: AdAnalysis[];
};

export default function AdAnalysisView({ analyses }: Props) {
  if (!analyses.length) return null;

  return (
    <section className="rounded-2xl bg-white/90 p-6 shadow-card">
      <h2 className="mb-3 text-2xl font-semibold">2) Analysis Output</h2>
      <div className="space-y-4">
        {analyses.map((item) => (
          <article key={item.image_id} className="rounded-xl border border-slate-200 p-4">
            <p className="mb-2 text-sm text-slate-500">{item.image_path}</p>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h3 className="font-semibold">Extracted Text</h3>
                <pre className="mt-2 overflow-auto rounded bg-slate-50 p-3 text-xs">
                  {JSON.stringify(item.extracted_text, null, 2)}
                </pre>
              </div>
              <div>
                <h3 className="font-semibold">Visual Description</h3>
                <pre className="mt-2 overflow-auto rounded bg-slate-50 p-3 text-xs">
                  {JSON.stringify(item.visual_description, null, 2)}
                </pre>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
