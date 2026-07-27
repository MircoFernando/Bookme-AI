import React from "react";
import ReactDOM from "react-dom/client";
import { ClerkProvider } from "@clerk/clerk-react";
import App from "./App";
import "./index.css";

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
const authDisabled = import.meta.env.VITE_AUTH_DISABLED === "true";

if (!authDisabled && !publishableKey) {
  throw new Error(
    "Missing VITE_CLERK_PUBLISHABLE_KEY. Set VITE_AUTH_DISABLED=true for local dev without Clerk.",
  );
}

const root = (
  <React.StrictMode>
    {authDisabled ? (
      <App authMode="dev" />
    ) : (
      <ClerkProvider publishableKey={publishableKey!} afterSignOutUrl="/">
        <App authMode="clerk" />
      </ClerkProvider>
    )}
  </React.StrictMode>
);

ReactDOM.createRoot(document.getElementById("root")!).render(root);
