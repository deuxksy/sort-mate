import { View, Text } from "react-native";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { Colors } from "@/constants/theme";
import type { ClassifyDetailResponse } from "@/types/classify";

interface ResultCardProps {
  result: ClassifyDetailResponse;
}

export function ResultCard({ result }: ResultCardProps) {
  return (
    <View className="mx-4 mt-4 p-5 bg-white rounded-2xl shadow-sm">
      <View className="flex-row items-center justify-between">
        <View className="flex-1">
          <Text className="text-sm text-gray-500">최종 분류</Text>
          <Text className="mt-1 text-xl font-bold text-gray-900">
            {result.confirmedClass}
          </Text>
        </View>
        <ConfidenceBadge confidence={result.confidence} />
      </View>

      {result.cached && (
        <Text className="mt-2 text-xs text-gray-400">캐시된 결과</Text>
      )}

      <Text className="mt-1 text-xs text-gray-400">
        출처: {result.source}
      </Text>
    </View>
  );
}
