import { View, ScrollView, Text } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import type { ClassifyDetailResponse } from "@/types/classify";
import { ResultCard } from "@/components/classify/ResultCard";
import { DisposalGuide } from "@/components/classify/DisposalGuide";
import { Button } from "@/components/ui/Button";
import { Colors } from "@/constants/theme";

export default function ResultScreen() {
  const router = useRouter();
  const { data } = useLocalSearchParams<{ data: string }>();

  if (!data) {
    return (
      <View className="flex-1 items-center justify-center bg-eco-bg">
        <Text className="text-gray-500">결과 데이터가 없습니다.</Text>
      </View>
    );
  }

  const result: ClassifyDetailResponse = JSON.parse(data);

  return (
    <ScrollView className="flex-1 bg-eco-bg">
      {/* 분류 결과 카드 */}
      <ResultCard result={result} />

      {/* 배출 방법 가이드 */}
      <DisposalGuide
        method={{
          steps: result.disposalMethod.notes,
          items: result.disposalMethod.items,
        }}
        costInfo={result.costInfo}
        warnings={result.warnings}
        regionSpecific={result.regionSpecific}
      />

      {/* 비용 정보 */}
      {result.costInfo && result.costInfo.type !== "FREE" && (
        <View className="mx-4 mt-4 p-4 bg-white rounded-xl">
          <Text className="text-sm font-semibold text-gray-800">비용 정보</Text>
          <Text className="mt-1 text-sm text-gray-600">
            {result.costInfo.amount} {result.costInfo.currency}
          </Text>
          {result.costInfo.collectionSchedule && (
            <Text className="mt-1 text-xs text-gray-500">
              수거일: {result.costInfo.collectionSchedule}
            </Text>
          )}
        </View>
      )}

      {/* 다시 촬영 버튼 */}
      <View className="mx-4 mt-6 mb-8">
        <Button
          onPress={() => router.back()}
          label="다시 촬영하기"
          icon="camera"
        />
      </View>
    </ScrollView>
  );
}
