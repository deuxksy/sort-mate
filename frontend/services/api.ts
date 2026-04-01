import { APP_CONFIG } from "@/constants/config";
import type { ClassifyDetailResponse } from "@/types/classify";

export async function classifyDetail(
  image: Blob,
  detectedClass: string | null,
  confidence: number,
  regionCode?: string,
): Promise<ClassifyDetailResponse> {
  const formData = new FormData();
  formData.append("image", image, "capture.jpg");
  formData.append("detectedClass", detectedClass ?? "");
  formData.append("confidence", String(confidence));
  if (regionCode) {
    formData.append("regionCode", regionCode);
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), APP_CONFIG.API_TIMEOUT_MS);

  try {
    const res = await fetch(`${APP_CONFIG.API_BASE_URL}/api/v1/classify/detail`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });

    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }

    return await res.json();
  } finally {
    clearTimeout(timeout);
  }
}
