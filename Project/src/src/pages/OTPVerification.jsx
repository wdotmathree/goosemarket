import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { createPageUrl } from "@/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, ArrowLeft, CheckCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function OTPVerification() {
  const navigate = useNavigate();
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [error, setError] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const inputRefs = useRef([]);

  const urlParams = new URLSearchParams(window.location.search);
  const email = urlParams.get('email');

  useEffect(() => {
    if (!email) {
      navigate(createPageUrl("Home"));
    }
  }, [email, navigate]);

  const handleChange = (index, value) => {
    if (value.length > 1) {
      value = value.slice(0, 1);
    }

    if (!/^\d*$/.test(value)) {
      return;
    }

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").slice(0, 6);
    if (!/^\d+$/.test(pastedData)) {
      return;
    }

    const newOtp = [...otp];
    for (let i = 0; i < pastedData.length && i < 6; i++) {
      newOtp[i] = pastedData[i];
    }
    setOtp(newOtp);

    const nextEmptyIndex = newOtp.findIndex(val => !val);
    if (nextEmptyIndex !== -1) {
      inputRefs.current[nextEmptyIndex]?.focus();
    } else {
      inputRefs.current[5]?.focus();
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError("");

    const otpValue = otp.join("");
    if (otpValue.length !== 6) {
      setError("Please enter the complete 6-digit code");
      return;
    }

    setIsVerifying(true);

    // Simulate verification (in real app, you'd call an API)
    setTimeout(() => {
      // Mock: accept any 6-digit code
      navigate(createPageUrl("Dashboard"));
    }, 1500);
  };

  const handleResend = () => {
    setError("");
    setOtp(["", "", "", "", "", ""]);
    inputRefs.current[0]?.focus();
    // In a real app, you'd trigger OTP resend API here
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

        {/* OTP Card */}
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-xl shadow-2xl">
          <CardHeader>
            <div className="flex items-center justify-between mb-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate(createPageUrl("Home"))}
                className="text-slate-400 hover:text-white"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <CheckCircle className="w-6 h-6 text-emerald-400" />
            </div>
            <CardTitle className="text-white">Verify Your Email</CardTitle>
            <CardDescription className="text-slate-400">
              We've sent a 6-digit code to <br />
              <span className="text-emerald-400 font-medium">{email}</span>
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert variant="destructive" className="mb-6 border-red-900 bg-red-950/50">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleVerify} className="space-y-6">
              {/* OTP Input Fields */}
              <div className="flex justify-center gap-2" onPaste={handlePaste}>
                {otp.map((digit, index) => (
                  <Input
                    key={index}
                    ref={(el) => (inputRefs.current[index] = el)}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(index, e)}
                    className="w-12 h-14 text-center text-2xl font-bold bg-slate-800 border-slate-700 text-white focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
                    autoFocus={index === 0}
                  />
                ))}
              </div>

              {/* Verify Button */}
              <Button
                type="submit"
                disabled={isVerifying}
                className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold shadow-lg shadow-emerald-500/20 h-12"
              >
                {isVerifying ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Verifying...
                  </div>
                ) : (
                  "Verify & Continue"
                )}
              </Button>
            </form>

            {/* Resend Link */}
            <div className="mt-6 text-center">
              <p className="text-slate-400 text-sm mb-2">Didn't receive the code?</p>
              <Button
                type="button"
                variant="link"
                onClick={handleResend}
                className="text-emerald-400 hover:text-emerald-300 p-0 h-auto"
              >
                Resend Code
              </Button>
            </div>

            {/* Info */}
            <div className="mt-6 pt-6 border-t border-slate-800">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/50">
                <span className="text-xl">💡</span>
                <p className="text-xs text-slate-400">
                  Check your spam folder if you don't see the email. The code expires in 10 minutes.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}