import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./index.css";

import Login from "./pages/Home.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Admin from "./pages/Admin.jsx";
import Layout from "./components/Layout.jsx";
import CreateEvent from "./pages/CreateEvent.jsx";
import Leaderboard from "./pages/Leaderboard.jsx";
import OTPVerification from "./pages/OTPVerification.jsx";

// ✅ import AuthProvider
import { AuthProvider } from "./context/AuthContext.jsx";

// Create a single QueryClient instance
const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>

            {/* Public Pages (NO NAVBAR) */}
            <Route path="/" element={<Login />} />
            <Route path="/OTPVerification" element={<OTPVerification />} />

            {/* Protected Pages (WITH NAVBAR / Layout) */}
            <Route
              path="/dashboard"
              element={
                <Layout>
                  <Dashboard />
                </Layout>
              }
            />

            <Route
              path="/create"
              element={
                <Layout>
                  <CreateEvent />
                </Layout>
              }
            />

            <Route
              path="/leaderboard"
              element={
                <Layout>
                  <Leaderboard />
                </Layout>
              }
            />

            <Route
              path="/admin"
              element={
                <Layout>
                  <Admin />
                </Layout>
              }
            />

          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
