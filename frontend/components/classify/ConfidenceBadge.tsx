import { View, Text } from "react-native";
import { Colors } from "@/constants/theme";

interface ConfidenceBadgeProps {
  confidence: number;
}

function getConfidenceLevel(confidence: number) {
  if (confidence >= 0.9) return { label: "매우 높음", color: Colors.primary };
  if (confidence >= 0.7) return { label: "높음", color: "#3b82f6" };
  if (confidence >= 0.5) return { label: "보통", color: "#f59e0b" };
  return { label: "낮음", color: Colors.error };
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const { label, color } = getConfidenceLevel(confidence);
  const percent = Math.round(confidence * 100);

  return (
    <View className="px-3 py-1.5 rounded-full" style={{ backgroundColor: color + "20" }}>
      <Text className="text-xs font-semibold" style={{ color }}>
        {label} {percent}%
      </Text>
    </View>
  );
}
