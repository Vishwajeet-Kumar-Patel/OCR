"use client";

import { useRef, useState } from "react";

type Props = {
  onUpload: (files: File[]) => Promise<void>;
  loading: boolean;
};

const MIN_UPLOAD_IMAGES = Number(process.env.NEXT_PUBLIC_MIN_UPLOAD_IMAGES ?? "5");
const MAX_UPLOAD_IMAGES = Number(process.env.NEXT_PUBLIC_MAX_UPLOAD_IMAGES ?? "10");

export default function AdUploader({ onUpload, loading }: Props) {
  const [files, setFiles] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const addFiles = (picked: FileList | null) => {
    if (!picked) return;
    const next = [...files, ...Array.from(picked)].slice(0, MAX_UPLOAD_IMAGES);
    setFiles(next);
  };

  const isUploadDisabled = loading || files.length < MIN_UPLOAD_IMAGES;
  const disabledReason = files.length < MIN_UPLOAD_IMAGES
    ? `Add at least ${MIN_UPLOAD_IMAGES} image(s) to enable upload.`
    : "";

  return (
    <section className="rounded-2xl bg-white/90 p-6 shadow-card">
      <h2 className="mb-2 text-2xl font-semibold">1) Upload Ad Images</h2>
      <p className="mb-4 text-sm text-slate-600">Upload {MIN_UPLOAD_IMAGES}-{MAX_UPLOAD_IMAGES} JPG/PNG images for style pattern extraction.</p>

      <div
        className="cursor-pointer rounded-xl border-2 border-dashed border-accent/40 bg-surface p-8 text-center"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          addFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
      >
        <p className="font-medium">Drag and drop images here</p>
        <p className="text-sm text-slate-500">or click to browse</p>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg"
        multiple
        className="hidden"
        onChange={(e) => addFiles(e.target.files)}
      />

      <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-5">
        {files.map((file, idx) => (
          <div key={`${file.name}-${idx}`} className="rounded-lg bg-slate-100 p-2 text-xs">
            <div className="truncate">{file.name}</div>
            <div className="text-slate-500">{Math.round(file.size / 1024)} KB</div>
          </div>
        ))}
      </div>

      <button
        disabled={isUploadDisabled}
        onClick={() => onUpload(files)}
        className="mt-4 rounded-lg bg-accent px-5 py-2 font-semibold text-white disabled:opacity-50"
      >
        {loading ? "Uploading..." : `Upload ${files.length} image(s)`}
      </button>
      {isUploadDisabled && !loading ? <p className="mt-2 text-xs text-slate-500">{disabledReason}</p> : null}
    </section>
  );
}
