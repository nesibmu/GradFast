import { createBrowserRouter } from "react-router";
import { Landing } from "./components/Landing";
import { Questions } from "./components/Questions";
import { Planner } from "./components/Planner";
import { Root } from "./components/Root";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Landing },
      { path: "questions", Component: Questions },
      { path: "planner", Component: Planner },
    ],
  },
]);
