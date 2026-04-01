const { getDefaultConfig } = "expo/metro-config";

import { withNativeWind } from "nativewind/metro";

const defaultConfig = getDefaultConfig(__dirname);

const config = defaultConfig;

module.exports = withNativeWind(config, {
  inlineRemoval: true,
});
