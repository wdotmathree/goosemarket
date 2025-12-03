import React, { useState, useRef, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { PlusCircle, Shield, Trophy, LayoutGrid, LogOut, CircleUserRound} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
	const location = useLocation();
	const { isAdmin, username, balance, userId } = useAuth();

	const [profilePopup, setProfilePopup] = useState(false);
	const profileRef = useRef(null);

	// Close popup when clicking outside
	useEffect(() => {
		const handleClickOutside = (event) => {
			if (profileRef.current && !profileRef.current.contains(event.target)) {
				setProfilePopup(false);
			}
		};

		if (profilePopup) {
			document.addEventListener("mousedown", handleClickOutside);
		}

		return () => {
			document.removeEventListener("mousedown", handleClickOutside);
		};
	}, [profilePopup]);

	const handleLogout = () => {
		document.location.replace("/api/auth/logout");
	};

	const navLink = (to, label, icon) => (
		<Link
			to={to}
			className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
				location.pathname === to ? "text-emerald-400" : "text-slate-300 hover:text-white"
			}`}
		>
			{icon}
			<span>{label}</span>
		</Link>
	);

	return (
		<>
			<nav className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-lg">
				<div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
					{/* Left section: Logo + Title */}
					<Link to="/dashboard">
						<div className="flex items-center gap-3">
							<img src="/goose.png" alt="GooseMarket Logo" className="w-10 h-10 rounded-xl" />
							<div>
								<h1 className="text-xl font-bold">GooseMarket</h1>
								<p className="text-slate-400 text-sm">UWaterloo Predictions</p>
							</div>
						</div>
					</Link>

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
								<p className="font-semibold text-emerald-400">
									{balance !== undefined && balance !== null
										? (balance/100).toLocaleString() + " G$"
										: "0 G$"}
								</p>
							</div>
						</div>

						<div className="relative" ref={profileRef}>
							<div
								className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center font-bold cursor-pointer select-none"
								onClick={() => setProfilePopup(!profilePopup)}
							>
								{username?.slice(0, 2).toUpperCase() ?? " "}
							</div>

							{/* Profile Dropdown Menu */}
							{profilePopup && (
								<div className="absolute right-0 mt-5 w-44 bg-slate-900 border border-slate-800 rounded-lg shadow-xl overflow-hidden">
									<Link
										to={`/user?id=${userId}`}
										className="w-full flex items-center gap-3 px-4 py-3 text-left text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
									>
										<CircleUserRound size={18}></CircleUserRound>
										<span>View Profile</span>
									</Link>
									<button
										onClick={handleLogout}
										className="w-full flex items-center gap-3 px-4 py-3 text-left text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
									>
										<LogOut size={18} />
										<span>Logout</span>
									</button>
								</div>
							)}
						</div>
					</div>
				</div>
			</nav>
		</>
	);
}
