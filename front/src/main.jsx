import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import WebContextProvider from "./store/website-context.jsx";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { BrowserRouter } from "react-router-dom";
import { GOOGLE_OAUTH_CLIENT_ID } from "./config";

// GoogleOAuthProvider must always wrap the tree because hooks like
// useGoogleLogin are called at component init. When no client ID is
// configured, pass a placeholder — the provider won't throw, and attempts
// to sign in will simply fail (expected when OAuth isn't set up).
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_OAUTH_CLIENT_ID || "not-configured"}>
      <BrowserRouter>
        <WebContextProvider>
          <App />
        </WebContextProvider>
      </BrowserRouter>
    </GoogleOAuthProvider>
  </React.StrictMode>
);
