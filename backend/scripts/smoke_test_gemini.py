import glob
import json
import requests

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    health = requests.get(f"{BASE_URL}/health", timeout=10)
    print("health", health.status_code, health.text)

    files = []
    handles = []
    for path in glob.glob("storage/test_images/*.png"):
        f = open(path, "rb")
        handles.append(f)
        files.append(("files", (path.split("\\")[-1], f, "image/png")))

    try:
        upload = requests.post(f"{BASE_URL}/ads/upload", files=files, timeout=30)
        print("upload", upload.status_code, upload.text)
    finally:
        for h in handles:
            h.close()

    if upload.status_code != 200:
        return

    job_id = upload.json()["job_id"]

    analyze = requests.post(f"{BASE_URL}/ads/analyze", json={"job_id": job_id}, timeout=420)
    print("analyze", analyze.status_code, analyze.text[:1200])

    patterns = requests.post(f"{BASE_URL}/ads/patterns", json={"job_id": job_id}, timeout=240)
    print("patterns", patterns.status_code, patterns.text[:1200])

    template = requests.post(f"{BASE_URL}/prompt/template", json={"job_id": job_id}, timeout=240)
    print("template", template.status_code, template.text[:1200])

    generate = requests.post(
        f"{BASE_URL}/prompt/generate",
        json={
            "job_id": job_id,
            "inputs": {
                "product_name": "HydraGlow Serum",
                "product_benefit": "deep hydration in 24 hours",
                "cta_text": "Shop Now",
                "target_audience": "women aged 22-35"
            }
        },
        timeout=120,
    )
    print("generate", generate.status_code, generate.text[:1200])


if __name__ == "__main__":
    main()
