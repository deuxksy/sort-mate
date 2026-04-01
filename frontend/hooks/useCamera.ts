import { useState, useCallback } from "react";
import { compressImage } from "@/services/image";
import { APP_CONFIG } from "@/constants/config";

interface UseCameraReturn {
  lastCaptureUri: string | null;
  capturing: boolean;
  capture: (uri: string) => Promise<string | null>;
}

export function useCamera(): UseCameraReturn {
  const [lastCaptureUri, setLastCaptureUri] = useState<string | null>(null);
  const [capturing, setCapturing] = useState(false);

  const capture = useCallback(async (uri: string) => {
    setCapturing(true);
    try {
      const { uri: compressed } = await compressImage(
        uri,
        APP_CONFIG.MAX_IMAGE_SIZE_BYTES / 1024,
      );
      setLastCaptureUri(compressed);
      return compressed;
    } catch {
      return null;
    } finally {
      setCapturing(false);
    }
  }, []);

  return { lastCaptureUri, capturing, capture };
}
