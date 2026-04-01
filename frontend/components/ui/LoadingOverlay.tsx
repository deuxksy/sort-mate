import { View, Text, ActivityIndicator } from "react-native";
import { Colors } from "@/constants/theme";

export function LoadingOverlay() {
  return (
    <View className="absolute inset-0 items-center justify-center bg-black/40">
      <View className="bg-white rounded-2xl p-6 items-center shadow-lg">
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text className="mt-3 text-sm text-gray-600">분석 중...</Text>
      </View>
    </View>
  );
}
