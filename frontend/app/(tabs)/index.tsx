import { View, Text, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { CameraView } from "@/components/camera/CameraView";
import { CaptureButton } from "@/components/camera/CaptureButton";
import { LoadingOverlay } from "@/components/ui/LoadingOverlay";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { useClassify } from "@/hooks/useClassify";
import { Colors } from "@/constants/theme";

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

      <View className="absolute bottom-8 left-0 right-0 items-center">
        <Text className="mb-3 text-sm text-gray-500">
          폐기물을 촬영해주세요
        </Text>
        <CaptureButton onPress={() => {}} loading={loading} />
      </View>
    </View>
  );
}
