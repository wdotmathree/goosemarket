import React from "react";
import { Link, useLocation } from "react-router-dom";
import { createPageUrl } from "@/utils";
import { LayoutDashboard, PlusCircle, Trophy, Shield, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function Layout({ children, currentPageName }) {
  const location = useLocation();
  const isAuthPage = location.pathname === createPageUrl("Home") || location.pathname === createPageUrl("OTPVerification");

  // Mock user data
  const mockUser = {
    name: "Alex Chen",
    balance: 1250,
    avatar: "AC"
  };

  if (isAuthPage) {
    return <div className="min-h-screen bg-slate-950">{children}</div>;
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <style>{`
        :root {
          --background: 222.2 84% 4.9%;
          --foreground: 210 40% 98%;
          --primary: 142.1 76.2% 36.3%;
          --primary-foreground: 355.7 100% 97.3%;
        }
        
        * {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .gradient-border {
          position: relative;
        }
        
        .gradient-border::before {
          content: '';
          position: absolute;
          inset: 0;
          border-radius: 12px;
          padding: 1px;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(139, 92, 246, 0.2));
          -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;
          mask-composite: exclude;
        }
      `}</style>

      {/* Navigation Bar */}
      <nav className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/95 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to={createPageUrl("Dashboard")} className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-violet-600 flex items-center justify-center transform group-hover:scale-105 transition-transform">
                <span className="text-2xl">🪿</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">GooseMarket</h1>
                <p className="text-xs text-slate-400">UWaterloo Predictions</p>
              </div>
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center gap-2">
              <Link to={createPageUrl("Dashboard")}>
                <Button
                  variant="ghost"
                  className={`text-slate-300 hover:text-white hover:bg-slate-800 ${
                    currentPageName === "Dashboard" ? "bg-slate-800 text-white" : ""
                  }`}
                >
                  <LayoutDashboard className="w-4 h-4 mr-2" />
                  Markets
                </Button>
              </Link>
              <Link to={createPageUrl("CreateEvent")}>
                <Button
                  variant="ghost"
                  className={`text-slate-300 hover:text-white hover:bg-slate-800 ${
                    currentPageName === "CreateEvent" ? "bg-slate-800 text-white" : ""
                  }`}
                >
                  <PlusCircle className="w-4 h-4 mr-2" />
                  Create
                </Button>
              </Link>
              <Link to={createPageUrl("Leaderboard")}>
                <Button
                  variant="ghost"
                  className={`text-slate-300 hover:text-white hover:bg-slate-800 ${
                    currentPageName === "Leaderboard" ? "bg-slate-800 text-white" : ""
                  }`}
                >
                  <Trophy className="w-4 h-4 mr-2" />
                  Leaderboard
                </Button>
              </Link>
              <Link to={createPageUrl("Admin")}>
                <Button
                  variant="ghost"
                  className={`text-slate-300 hover:text-white hover:bg-slate-800 ${
                    currentPageName === "Admin" ? "bg-slate-800 text-white" : ""
                  }`}
                >
                  <Shield className="w-4 h-4 mr-2" />
                  Admin
                </Button>
              </Link>
            </div>

            {/* User Section */}
            <div className="flex items-center gap-4">
              <div className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">💰</span>
                  <div>
                    <p className="text-xs text-slate-400">Balance</p>
                    <p className="text-sm font-bold text-emerald-400">
                      {mockUser.balance.toLocaleString()} G$
                    </p>
                  </div>
                </div>
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white font-semibold">
                {mockUser.avatar}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="min-h-[calc(100vh-73px)]">
        {children}
      </main>
    </div>
  );
}
