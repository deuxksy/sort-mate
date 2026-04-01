export const APP_CONFIG = {
  API_BASE_URL: process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8080",
  API_TIMEOUT_MS: 10_000,
  MAX_IMAGE_SIZE_BYTES: 1_024 * 1_024, // 1MB
  YOLO_CONFIDENCE_THRESHOLD: 0.7,
  YOLO_MODEL_PATH: "models/waste_v4.tflite",
} as const;
