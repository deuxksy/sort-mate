import { View, Text, Pressable } from "react-native";
import { launchCameraAsync, requestCameraPermissionsAsync } from "expo-image-picker";
import { useState } from "react";
import { Colors } from "@/constants/theme";

interface CameraViewProps {
  onCapture?: (uri: string) => void;
  disabled?: boolean;
}

export function CameraView({ onCapture, disabled }: CameraViewProps) {
  const [status, setStatus] = useState<"idle" | "denied">("idle");

  const openCamera = async () => {
    if (disabled) return;

    const perm = await requestCameraPermissionsAsync();
    if (!perm.granted) {
      setStatus("denied");
      return;
    }
    setStatus("idle");

    const result = await launchCameraAsync({
      mediaTypes: ["images"],
      quality: 0.8,
      allowsEditing: false,
    });

    if (!result.canceled && result.assets?.[0]?.uri) {
      onCapture?.(result.assets[0].uri);
    }
  };

  if (status === "denied") {
    return (
      <View className="flex-1 items-center justify-center bg-eco-bg px-6">
        <Text className="text-gray-600 mb-4 text-center">
          카메라 접근이 거부되었습니다.{"\n"}브라우저 설정에서 카메라를 허용해주세요.
        </Text>
        <Pressable
          onPress={() => setStatus("idle")}
          className="px-6 py-3 rounded-xl"
          style={{ backgroundColor: Colors.primary }}
        >
          <Text className="text-white font-semibold">다시 시도</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View className="flex-1 items-center justify-center bg-eco-bg">
      <Pressable
        onPress={openCamera}
        disabled={disabled}
        className="items-center gap-4"
      >
        <View
          className="w-20 h-20 rounded-full items-center justify-center"
          style={{ backgroundColor: Colors.primary }}
        >
          <Text className="text-4xl">📷</Text>
        </View>
        <Text className="text-gray-500 text-sm">탭하여 촬영</Text>
      </Pressable>
    </View>
  );
}
