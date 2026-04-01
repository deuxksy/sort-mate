import { APP_CONFIG } from "@/constants/config";
import type { YOLOResult } from "@/types/classify";

/**
 * YOLO TFLite 온디바이스스 분류 스텁.
 * Phase 2에서 실제 TFLite runtime으로 교체.
 */
export async function classifyOnDevice(_imageUri: string): Promise<YOLOResult> {
  return {
    className: "unknown",
    confidence: 0,
    boundingBox: [0, 0, 0, 0],
  };
}

export function isModelReady(): boolean {
  return false;
}
