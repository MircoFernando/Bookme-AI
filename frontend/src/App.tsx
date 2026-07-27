import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import ChatApp from "@/pages/ChatApp";

type AuthMode = "dev" | "clerk";

export default function App({ authMode }: { authMode: AuthMode }) {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage authMode={authMode} />} />
        <Route path="/app" element={<ChatApp authMode={authMode} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
