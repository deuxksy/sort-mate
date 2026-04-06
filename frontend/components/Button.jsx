import React from "react";
import { TouchableOpacity, Text } from "react-native";

export function Button({
  variant = "primary",
  size = "md",
  children,
  onPress,
  disabled = false,
}) {
  const baseClasses = "rounded-lg font-semibold items-center justify-center";

  const variantClasses = {
    primary: "bg-primary text-white",
    secondary: "bg-gray-200 text-gray-800",
    outline: "border-2 border-primary text-primary",
  };

  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
  };

  const safeVariant = variantClasses[variant] ? variant : "primary";
  const safeSize = sizeClasses[size] ? size : "md";

  return (
    <TouchableOpacity
      className={`${baseClasses} ${variantClasses[safeVariant]} ${sizeClasses[safeSize]}`}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.7}
    >
      <Text className="font-semibold">{children}</Text>
    </TouchableOpacity>
  );
}
