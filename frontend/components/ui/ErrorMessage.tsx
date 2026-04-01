import { View, Text, Pressable } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "@/constants/theme";

interface ErrorMessageProps {
  message: string;
  onDismiss: () => void;
}

export function ErrorMessage({ message, onDismiss }: ErrorMessageProps) {
  return (
    <View className="mx-4 mt-2 p-3 bg-red-50 rounded-xl flex-row items-center">
      <Ionicons name="alert-circle" size={20} color={Colors.error} />
      <Text className="flex-1 ml-2 text-sm text-red-700">{message}</Text>
      <Pressable onPress={onDismiss}>
        <Ionicons name="close" size={18} color="#999" />
      </Pressable>
    </View>
  );
}
