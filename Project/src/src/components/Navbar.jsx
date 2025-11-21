import React from "react";
import { Link, useLocation } from "react-router-dom";
import { PlusCircle, Shield, Trophy, LayoutGrid } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const location = useLocation();
  const { isAdmin } = useAuth();

  const navLink = (to, label, icon) => (
    <Link
      to={to}
      className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
        location.pathname === to
          ? "text-emerald-400"
          : "text-slate-300 hover:text-white"
      }`}
    >
      {icon}
      <span>{label}</span>
    </Link>
  );

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">

        {/* Left section: Logo + Title */}
        <div className="flex items-center gap-3">
          <img
            src="/goose.png"
            alt="GooseMarket Logo"
            className="w-10 h-10 rounded-xl"
          />
          <div>
            <h1 className="text-xl font-bold">GooseMarket</h1>
            <p className="text-slate-400 text-sm">UWaterloo Predictions</p>
          </div>
        </div>

        {/* Center section: Navigation Links */}
        <div className="hidden md:flex items-center gap-6">
          {navLink("/dashboard", "Markets", <LayoutGrid size={18} />)}
          {navLink("/create", "Create", <PlusCircle size={18} />)}
          {navLink("/leaderboard", "Leaderboard", <Trophy size={18} />)}

          {/* Only show Admin link if logged in as admin */}
          {isAdmin && navLink("/admin", "Admin", <Shield size={18} />)}
        </div>

        {/* Right section: Balance + Avatar */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-2 rounded-xl">
            <span className="text-yellow-400 text-lg">💰</span>
            <div>
              <p className="text-xs text-slate-400">Balance</p>
              <p className="font-semibold text-emerald-400">1,250 G$</p>
            </div>
          </div>

          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center font-bold">
            AC
          </div>
        </div>
      </div>
    </nav>
  );
}
