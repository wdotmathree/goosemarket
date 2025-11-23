import React, { useState, useEffect } from "react";
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

export default function Login() {
	const navigate = useNavigate();
	const authContext = useAuth();

	const [activeTab, setActiveTab] = useState("login");
	const [error, setError] = useState("");

	// Login state
	const [loginEmail, setLoginEmail] = useState("");
	const [loginPassword, setLoginPassword] = useState("");
	const [update, setUpdate] = useState(false);

	// Sign up state
	const [signupEmail, setSignupEmail] = useState("");
	const [signupPassword, setSignupPassword] = useState("");
	const [signupUsername, setSignupUsername] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [submitTime, setSubmitTime] = useState(0);
	const [currentTime, setCurrentTime] = useState(0);
	var timeInterval = null;

	// Verify email
	const [verifyEmail, setVerifyEmail] = useState("");

	const validateEmail = (email) => {
		return !email.includes("+") && email.endsWith("@uwaterloo.ca");
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

		fetch("/api/auth/login", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				email: loginEmail,
				password: loginPassword,
			}),
		})
			.then((res) => {
				if (res.ok) {
					setUpdate(true);
				}
				return res.json();
			})
			.then((data) => {
				setError(data["error"] || "Login failed");
			});
	};

	const handleSignup = async (e) => {
		e.preventDefault();
		setError("");

		console.log(signupEmail, signupPassword, confirmPassword);

		if (!validateEmail(signupEmail)) {
			setError("Please use your @uwaterloo.ca email address without any '+' symbols");
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

		fetch("/api/auth/register", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				email: signupEmail,
				password: signupPassword,
				username: signupUsername,
			}),
		})
			.then((res) => {
				if (res.ok) {
					setVerifyEmail(signupEmail);
					setSubmitTime(window.performance.now());
				}
				return res.json();
			})
			.then((data) => {
				setError(data["error"] || "Registration failed");
			});
	};

	// Detect email verification token in URL hash
	useEffect(() => {
		if (document.cookie.includes("user-info")) {
			authContext.setUpdate(true);
			navigate("/dashboard");
			return;
		}

		if (window.location.hash.startsWith("#access_token")) {
			let obj = {};
			window.location.hash
				.substring(1)
				.split("&")
				.forEach((part) => {
					const [key, value] = part.split("=");
					obj[key] = value;
				});

			window.history.replaceState(null, "", window.location.pathname);

			fetch("/api/auth/verify", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(obj),
			})
				.then((res) => {
					if (res.ok) navigate("/dashboard");
					return res.json();
				})
				.then((data) => {
					setError(data["error"] || "Email verification failed");
				});
		}

		if (timeInterval === null) {
			timeInterval = setInterval(() => {
				setCurrentTime(window.performance.now());
			}, 100);
		}

		setUpdate(false);
	}, [navigate, update]);

	const wrapSetActiveTab = (tab) => {
		setError("");
		setActiveTab(tab);
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
					{verifyEmail ? (
						<>
							<CardHeader>
								<CardTitle className="text-white">Email Verification</CardTitle>
							</CardHeader>
							<CardContent>
								<h2 className="text-slate-300 mb-4">Thank you for registering for GooseMarket!</h2>
								<p className="text-slate-300 mb-4">
									An email has been sent to {verifyEmail}. Please click the link to continue.
								</p>
								<p className="text-slate-300 mb-4">This tab can now be closed</p>
								{window.performance.now() - submitTime > 60000 ? (
									<Button
										className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold shadow-lg shadow-emerald-500/20"
										onClick={handleSignup}
									>
										Resend Verification Link
									</Button>
								) : (
									<Button
										className="w-full text-white font-semibold bg-slate-800 hover:bg-slate-800 cursor-default"
										disabled
									>
										Resend Verification Link ({Math.ceil(60 - (currentTime - submitTime) / 1000)}s)
									</Button>
								)}
							</CardContent>
						</>
					) : (
						<>
							<CardHeader>
								<CardTitle className="text-white">
									{activeTab === "admin" ? "Admin Access" : "Welcome"}
								</CardTitle>
								<CardDescription className="text-slate-400">
									{activeTab === "login" && "Sign in with your UWaterloo email"}
									{activeTab === "signup" && "Create your GooseMarket account"}
								</CardDescription>
							</CardHeader>
							<CardContent>
								<Tabs value={activeTab} onValueChange={wrapSetActiveTab} className="w-full">
									<TabsList className="grid w-full grid-cols-2 bg-slate-800 mb-6">
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
												<Label htmlFor="login-email" className="text-slate-300">
													Email <span className="text-red-500">*</span>
												</Label>
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
												<Label htmlFor="login-password" className="text-slate-300">
													Password <span className="text-red-500">*</span>
												</Label>
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
												className="text-emerald-500 hover:text-emerald-300 p-0 h-auto"
											>
												Forgot password?
											</Button>
											<Button
												type="submit"
												className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold shadow-lg shadow-emerald-500/20"
											>
												Sign In
											</Button>
										</form>
									</TabsContent>

									{/* Sign Up Tab */}
									<TabsContent value="signup">
										<form onSubmit={handleSignup} className="space-y-4">
											<div className="space-y-2">
												<Label htmlFor="signup-email" className="text-slate-300">
													Email <span className="text-red-500">*</span>
												</Label>
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
												<Label htmlFor="signup-username" className="text-slate-300">
													Username
												</Label>
												<Input
													id="signup-username"
													type="text"
													placeholder="Enter your username"
													value={signupUsername}
													onChange={(e) => setSignupUsername(e.target.value)}
													className="bg-slate-800 border-slate-700 text-white focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
												/>
											</div>
											<div className="space-y-2">
												<Label htmlFor="signup-password" className="text-slate-300">
													Password <span className="text-red-500">*</span>
												</Label>
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
												<Label htmlFor="confirm-password" className="text-slate-300">
													Confirm Password <span className="text-red-500">*</span>
												</Label>
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
								</Tabs>

								<div className="mt-6 pt-6 border-t border-slate-800">
									<p className="text-xs text-slate-500 text-center">
										By continuing, you agree to GooseMarket's Terms of Service and Privacy Policy
									</p>
								</div>
							</CardContent>
						</>
					)}
				</Card>
			</div>
		</div>
	);
}
