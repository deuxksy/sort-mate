import { manipulateAsync, SaveFormat } from "expo-image-manipulator";
import { APP_CONFIG } from "@/constants/config";

export async function compressImage(
  uri: string,
  maxWidth = 1024,
): Promise<{ uri: string; blob: Blob }> {
  const result = await manipulateAsync(
    uri,
    [{ resize: { width: maxWidth } }],
    { compress: 0.8, format: SaveFormat.JPEG },
  );

  const response = await fetch(result.uri);
  const blob = await response.blob();

  // 1MB 초과 시 추가 압축
  if (blob.size > APP_CONFIG.MAX_IMAGE_SIZE_BYTES) {
    const recompressed = await manipulateAsync(
      result.uri,
      [{ resize: { width: maxWidth * 0.7 } }],
      { compress: 0.6, format: SaveFormat.JPEG },
    );
    const retryResponse = await fetch(recompressed.uri);
    const retryBlob = await retryResponse.blob();
    return { uri: recompressed.uri, blob: retryBlob };
  }

  return { uri: result.uri, blob };
}
