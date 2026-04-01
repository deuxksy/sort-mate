import { Pressable, Text, ActivityIndicator } from "react-native";
import { Colors } from "@/constants/theme";

interface ButtonProps {
  onPress: () => void;
  label: string;
  icon?: string;
  loading?: boolean;
  variant?: "primary" | "outline";
}

export function Button({ onPress, label, icon, loading, variant = "primary" }: ButtonProps) {
  const isPrimary = variant === "primary";

  return (
    <Pressable
      onPress={onPress}
      disabled={loading}
      className="flex-row items-center justify-center py-3.5 px-6 rounded-xl"
      style={{
        backgroundColor: isPrimary ? Colors.primary : "transparent",
        borderWidth: isPrimary ? 0 : 1.5,
        borderColor: Colors.primary,
      }}
    >
      {loading ? (
        <ActivityIndicator color={isPrimary ? "#fff" : Colors.primary} />
      ) : (
        <>
          {icon && (
            <Text
              className="mr-2"
              style={{ color: isPrimary ? "#fff" : Colors.primary, fontSize: 18 }}
            >
              {icon}
            </Text>
          )}
          <Text
            className="font-semibold text-base"
            style={{ color: isPrimary ? "#fff" : Colors.primary }}
          >
            {label}
          </Text>
        </>
      )}
    </Pressable>
  );
}
