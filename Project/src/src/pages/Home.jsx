import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createPageUrl } from "@/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

// Import Auth Context
import { useAuth } from "@/context/AuthContext";

export default function Home() {
  const navigate = useNavigate();
  const { setIsAdmin } = useAuth();

  const [activeTab, setActiveTab] = useState("login");
  const [error, setError] = useState("");

  // Login state
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Sign up state
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Admin login state
  const [adminUsername, setAdminUsername] = useState("");
  const [adminPassword, setAdminPassword] = useState("");

  const validateEmail = (email) => {
    return email.endsWith("@uwaterloo.ca");
  };

  const handleLogin = (e) => {
    e.preventDefault();
    setError("");

    if (!validateEmail(loginEmail)) {
      setError("Please use your @uwaterloo.ca email address");
      return;
    }

    if (!loginPassword) {
      setError("Please enter your password");
      return;
    }

    // Ensure normal users are NOT admins
    setIsAdmin(false);

    navigate(createPageUrl("Dashboard"));
  };

  const handleSignup = (e) => {
    e.preventDefault();
    setError("");

    if (!validateEmail(signupEmail)) {
      setError("Please use your @uwaterloo.ca email address");
      return;
    }

    if (!signupPassword || signupPassword.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (signupPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Normal signup users are NOT admins
    setIsAdmin(false);

    navigate(createPageUrl(`OTPVerification?email=${encodeURIComponent(signupEmail)}`));
  };

  const handleAdminLogin = (e) => {
    e.preventDefault();
    setError("");

    if (adminUsername !== "1234" || adminPassword !== "1234") {
      setError("Invalid admin credentials");
      return;
    }

    // Mark as admin
    setIsAdmin(true);

    navigate(createPageUrl("Admin"));
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="w-full max-w-md">
        {/* Logo Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500 to-violet-600 mb-4 shadow-2xl shadow-emerald-500/20">
            <span className="text-5xl">🪿</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">GooseMarket</h1>
          <p className="text-slate-400">UWaterloo Campus Prediction Market</p>
        </div>

        {/* Auth Card */}
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-xl shadow-2xl">
          <CardHeader>
            <CardTitle className="text-white">
              {activeTab === "admin" ? "Admin Access" : "Welcome"}
            </CardTitle>
            <CardDescription className="text-slate-400">
              {activeTab === "login" && "Sign in with your UWaterloo email"}
              {activeTab === "signup" && "Create your GooseMarket account"}
              {activeTab === "admin" && "Admin access only"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-3 bg-slate-800 mb-6">
                <TabsTrigger 
                  value="login" 
                  className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white"
                >
                  Login
                </TabsTrigger>
                <TabsTrigger 
                  value="signup" 
                  className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white"
                >
                  Sign Up
                </TabsTrigger>
                <TabsTrigger 
                  value="admin" 
                  className="data-[state=active]:bg-violet-600 data-[state=active]:text-white"
                >
                  Admin
                </TabsTrigger>
              </TabsList>

              {error && (
                <Alert variant="destructive" className="mb-4 border-red-900 bg-red-950/50">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Login Tab */}
              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email" className="text-slate-300">Email</Label>
                    <Input
                      id="login-email"
                      type="email"
                      placeholder="user@uwaterloo.ca"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="login-password" className="text-slate-300">Password</Label>
                    <Input
                      id="login-password"
                      type="password"
                      placeholder="••••••••"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      className="bg-slate-800 border-slate-700 text-white focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
                      required
                    />
                  </div>
                  <Button
                    type="button"
                    variant="link"
                    className="text-emerald-400 hover:text-emerald-300 p-0 h-auto"
                  >
                    Forgot password?
                  </Button>
                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold shadow-lg shadow-emerald-500/20"
                  >
                    Sign In
                  </Button>

                  <div className="pt-4 text-center">
                    <button
                      type="button"
                      onClick={() => setActiveTab("admin")}
                      className="text-sm text-slate-400 hover:text-violet-400 transition-colors"
                    >
                      Are you an admin? <span className="underline">Click here</span>
                    </button>
                  </div>
                </form>
              </TabsContent>

              {/* Sign Up Tab */}
              <TabsContent value="signup">
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="signup-email" className="text-slate-300">Email</Label>
                    <Input
                      id="signup-email"
                      type="email"
                      placeholder="user@uwaterloo.ca"
                      value={signupEmail}
                      onChange={(e) => setSignupEmail(e.target.value)}
                      className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password" className="text-slate-300">Password</Label>
                    <Input
                      id="signup-password"
                      type="password"
                      placeholder="••••••••"
                      value={signupPassword}
                      onChange={(e) => setSignupPassword(e.target.value)}
                      className="bg-slate-800 border-slate-700 text-white focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirm-password" className="text-slate-300">Confirm Password</Label>
                    <Input
                      id="confirm-password"
                      type="password"
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="bg-slate-800 border-slate-700 text-white focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
                      required
                    />
                  </div>
                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold shadow-lg shadow-emerald-500/20"
                  >
                    Continue
                  </Button>
                </form>
              </TabsContent>

              {/* Admin Login Tab */}
              <TabsContent value="admin">
                <form onSubmit={handleAdminLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="admin-username" className="text-slate-300">Username</Label>
                    <Input
                      id="admin-username"
                      type="text"
                      placeholder="Enter admin username"
                      value={adminUsername}
                      onChange={(e) => setAdminUsername(e.target.value)}
                      className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="admin-password" className="text-slate-300">Password</Label>
                    <Input
                      id="admin-password"
                      type="password"
                      placeholder="••••••••"
                      value={adminPassword}
                      onChange={(e) => setAdminPassword(e.target.value)}
                      className="bg-slate-800 border-slate-700 text-white focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all"
                      required
                    />
                  </div>
                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-violet-500 to-violet-600 hover:from-violet-600 hover:to-violet-700 text-white font-semibold shadow-lg shadow-violet-500/20"
                  >
                    Admin Sign In
                  </Button>

                  <div className="pt-4 text-center">
                    <button
                      type="button"
                      onClick={() => setActiveTab("login")}
                      className="text-sm text-slate-400 hover:text-emerald-400 transition-colors"
                    >
                      Back to user login
                    </button>
                  </div>
                </form>
              </TabsContent>
            </Tabs>

            <div className="mt-6 pt-6 border-t border-slate-800">
              <p className="text-xs text-slate-500 text-center">
                By continuing, you agree to GooseMarket's Terms of Service and Privacy Policy
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
