import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./index.css";

import Login from "./pages/Home.jsx";
import OTPVerification from "./pages/OTPVerification.jsx";

// NEW imports for this branch
import Dashboard from "./pages/Dashboard.jsx";
import Layout from "./components/Layout.jsx";

import { AuthProvider } from "./context/AuthContext.jsx";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>

            {/* Public routes */}
            <Route path="/" element={<Login />} />
            <Route path="/OTPVerification" element={<OTPVerification />} />

            {/* Dashboard route (includes Layout + Navbar automatically) */}
            <Route
              path="/dashboard"
              element={
                <Layout>
                  <Dashboard />
                </Layout>
              }
            />
            <Route
  path="/event/:id"
  element={
    <Layout>
      <EventDetail />
    </Layout>
  }
/>


          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
