import { Stack } from "expo-router";
import { Colors } from "@/constants/theme";

export default function ClassifyLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: Colors.background },
        headerTintColor: Colors.primaryDarker,
      }}
    />
  );
}
