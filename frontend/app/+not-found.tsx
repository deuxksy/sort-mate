import { Link, Stack } from "expo-router";
import { Text, View } from "react-native";

export default function NotFoundScreen() {
  return (
    <>
      <Stack.Screen options={{ title: "Oops!" }} />
      <View className="flex-1 items-center justify-center p-5">
        <Text className="text-xl font-bold text-gray-800">
          이 화면은 존재하지 않습니다.
        </Text>
        <Link href="/" className="mt-4 text-primary">
          <Text className="text-primary font-semibold">홈으로 돌아가기</Text>
        </Link>
      </View>
    </>
  );
}
