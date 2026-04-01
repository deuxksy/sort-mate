import { View, Text } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "@/constants/theme";
import type { DisposalItemResponse } from "@/types/classify";

interface DisposalGuideProps {
  method?: { steps: string[]; items?: DisposalItemResponse[] };
  costInfo?: { type: string; amount: number; currency: string; collectionSchedule?: string };
  warnings?: string[];
  regionSpecific?: string;
}

export function DisposalGuide({ method, costInfo, warnings, regionSpecific }: DisposalGuideProps) {
  if (!method && !warnings?.length && !regionSpecific) return null;

  return (
    <View className="mx-4 mt-4 p-5 bg-white rounded-2xl shadow-sm">
      <Text className="text-base font-semibold text-gray-800">배출 방법</Text>

      {method?.steps && method.steps.length > 0 && (
        <View className="mt-3">
          {method.steps.map((step, i) => (
            <View key={i} className="flex-row items-start mt-2">
              <View className="w-6 h-6 rounded-full items-center justify-center mr-2 mt-0.5"
                style={{ backgroundColor: Colors.primary + "20" }}>
                <Text className="text-xs font-bold" style={{ color: Colors.primary }}>
                  {i + 1}
                </Text>
              </View>
              <Text className="flex-1 text-sm text-gray-700">{step}</Text>
            </View>
          ))}
        </View>
      )}

      {warnings && warnings.length > 0 && (
        <View className="mt-4 p-3 bg-amber-50 rounded-lg">
          <View className="flex-row items-center mb-1">
            <Ionicons name="warning" size={16} color="#f59e0b" />
            <Text className="ml-1 text-sm font-semibold text-amber-700">주의사항</Text>
          </View>
          {warnings.map((w, i) => (
            <Text key={i} className="text-xs text-amber-600 mt-1">• {w}</Text>
          ))}
        </View>
      )}

      {regionSpecific && (
        <Text className="mt-3 text-xs text-gray-400">
          지역 정보: {regionSpecific}
        </Text>
      )}
    </View>
  );
}
