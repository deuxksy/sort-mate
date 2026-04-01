import { useRef } from "react";
import { View, Text, Pressable } from "react-native";
import {
  CameraView as ExpoCameraView,
  useCameraPermissions,
} from "expo-camera";
import { Colors } from "@/constants/theme";

interface CameraViewProps {
  onCapture?: (uri: string) => void;
  disabled?: boolean;
}

export function CameraView({ disabled }: CameraViewProps) {
  const cameraRef = useRef<ExpoCameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();

  if (!permission?.granted) {
    return (
      <View className="flex-1 items-center justify-center bg-eco-bg">
        <Text className="text-gray-600 mb-4">
          {permission?.status === "denied"
            ? "카메라 접근이 거부되었습니다. 설정에서 허용해주세요."
            : "카메라 권한이 필요합니다."}
        </Text>
        <Pressable
          onPress={requestPermission}
          className="px-6 py-3 rounded-xl"
          style={{ backgroundColor: Colors.primary }}
        >
          <Text className="text-white font-semibold">
            {permission?.status === "denied" ? "설정 열기" : "권한 요청"}
          </Text>
        </Pressable>
      </View>
    );
  }

  return (
    <ExpoCameraView
      ref={cameraRef}
      className="flex-1"
      facing="back"
    />
  );
}
