import { View } from "react-native";
import { useRouter } from "expo-router";
import { CameraView } from "@/components/camera/CameraView";
import { LoadingOverlay } from "@/components/ui/LoadingOverlay";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { useClassify } from "@/hooks/useClassify";

export default function HomeScreen() {
  const router = useRouter();
  const { loading, error, classify, clearError } = useClassify();

  const handleCapture = async (uri: string) => {
    const result = await classify(uri);
    if (result) {
      router.push({
        pathname: "/classify/result",
        params: { data: JSON.stringify(result) },
      });
    }
  };

  return (
    <View className="flex-1 bg-eco-bg">
      {error && <ErrorMessage message={error} onDismiss={clearError} />}
      <CameraView onCapture={handleCapture} disabled={loading} />
      {loading && <LoadingOverlay />}
    </View>
  );
}
