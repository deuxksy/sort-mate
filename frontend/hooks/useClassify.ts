import { useState, useCallback } from "react";
import { classifyDetail } from "@/services/api";
import { compressImage } from "@/services/image";
import { APP_CONFIG } from "@/constants/config";
import type { ClassifyDetailResponse } from "@/types/classify";

interface UseClassifyReturn {
  loading: boolean;
  error: string | null;
  result: ClassifyDetailResponse | null;
  classify: (imageUri: string) => Promise<ClassifyDetailResponse | null>;
  clearError: () => void;
}

export function useClassify(): UseClassifyReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ClassifyDetailResponse | null>(null);

  const classify = useCallback(async (imageUri: string) => {
    setLoading(true);
    setError(null);

    try {
      const { uri: compressed, blob } = await compressImage(
        imageUri,
        APP_CONFIG.MAX_IMAGE_SIZE_BYTES / 1024,
      );

      const response = await classifyDetail(blob, null, 0);
      setResult(response);
      return response;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "분류 요청에 실패했습니다.";
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return { loading, error, result, classify, clearError };
}
