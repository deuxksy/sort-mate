import { Pressable, Text, View } from "react-native";
import { Colors } from "@/constants/theme";

interface CaptureButtonProps {
  onPress: () => void;
  loading?: boolean;
  label?: string;
}

export function CaptureButton({ onPress, loading, label }: CaptureButtonProps) {
  return (
    <Pressable
      onPress={onPress}
      disabled={loading}
      className="w-16 h-16 rounded-full items-center justify-center"
      style={{ backgroundColor: Colors.primary }}
      accessibilityLabel={label ?? "촬영"}
      accessibilityRole="button"
    >
      <View className="w-14 h-14 rounded-full border-2 border-white" />
    </Pressable>
  );
}
