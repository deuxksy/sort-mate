import React from "react";
import { Button } from "../components/Button";

const meta = {
  title: "Components/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "outline"],
    },
    size: {
      control: "select",
      options: ["sm", "md", "lg"],
    },
    onPress: { action: "clicked" },
  },
};
export default meta;

export const Primary = {
  args: { variant: "primary", children: "버리 분류하기" },
};
export const Secondary = {
  args: { variant: "secondary", children: "취소" },
};
export const Outline = {
  args: { variant: "outline", children: "다시 분석" },
};
export const AllVariants = {
  render: (args) => React.createElement("div", { style: { display: "flex", gap: 8 } },
    React.createElement(Button, { ...args, variant: "primary", children: "버리 분류하기" }),
    React.createElement(Button, { ...args, variant: "secondary", children: "취소" }),
    React.createElement(Button, { ...args, variant: "outline", children: "다시 분석" })
  ),
};
