import React, { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  Target,
  AlertTriangle
} from "lucide-react";

export default function Profile() {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get("id");

    const [openSection, setOpenSection] = useState(true);
    const [closedSection, setClosedSection] = useState(true);
    // State for user data to allow reset on id change
    const [user, setUser] = useState({});
    const [showSkeleton, setShowSkeleton] = useState(false);
    const prevUserId = useRef(userId);

  // Fetch profile data from backend
  const {
    data,
    isLoading,
    isFetching,
    refetch,
  } = useQuery({
    queryKey: ["userProfile", userId],
    queryFn: async () => {
      const response = await fetch(`/api/user`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId })
      });
      if (!response.ok) {
        throw new Error("Failed to fetch user profile");
      }
      return response.json();
    },
    enabled: !!userId,
    refetchOnWindowFocus: false,
    // cacheTime: 0, // Optionally, do not cache
  });

  // Effect: reset user data and show skeleton as soon as userId changes
  useEffect(() => {
    if (prevUserId.current !== userId) {
      setUser({});
      setShowSkeleton(true);
      prevUserId.current = userId;
    }
  }, [userId]);

  // Effect: when data is fetched, update user and hide skeleton
  useEffect(() => {
    if (data) {
      setUser(data);
      setShowSkeleton(false);
    }
  }, [data]);

  // Show skeleton if loading or fetching or showSkeleton is true
  const shouldShowSkeleton = isLoading || isFetching || showSkeleton;

  const isProfitable = (user.lifetime_pnl ?? 0) >= 0;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-4xl mx-auto px-6 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Profile</h1>
          <p className="text-slate-400">{user.username}'s trading statistics and positions</p>
        </div>

        {shouldShowSkeleton ? (
          <div className="space-y-6">
            <Skeleton className="h-32 w-full bg-slate-800" />
            <Skeleton className="h-48 w-full bg-slate-800" />
          </div>
        ) : (
          <>
            {/* Username Card */}
            <Card className="border-slate-800 bg-slate-900/50 mb-6">
              <CardContent className="p-6 pt-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-2xl font-bold">
                    {user.username?.slice(0, 2).toUpperCase() || "??"}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">
                      {user.username}
                    </h2>
                    <p className="text-slate-400">Trader</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4 mb-8">
              
              {/* Balance */}
              <Card className="border-slate-800 bg-slate-900/50">
                <CardContent className="p-4 pt-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-emerald-500/10">
                      <Wallet className="w-6 h-6 text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs">Balance</p>
                      <p className="text-xl font-bold text-white">
                        {user.balance?.toLocaleString()} G$
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Lifetime PnL */}
              <Card className="border-slate-800 bg-slate-900/50">
                <CardContent className="p-4 pt-4">
                  <div className="flex items-center gap-3">
                    <div
                      className={`p-2 rounded-lg ${
                        isProfitable ? "bg-emerald-500/10" : "bg-red-500/10"
                      }`}
                    >
                      {isProfitable ? (
                        <TrendingUp className="w-6 h-6 text-emerald-400" />
                      ) : (
                        <TrendingDown className="w-6 h-6 text-red-400" />
                      )}
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs">Lifetime PnL</p>
                      <p
                        className={`text-xl font-bold ${
                          isProfitable ? "text-emerald-400" : "text-red-400"
                        }`}
                      >
                        {isProfitable ? "+" : ""}
                        {user.lifetime_pnl?.toLocaleString()} G$
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Exposure */}
              <Card className="border-slate-800 bg-slate-900/50">
                <CardContent className="p-4 pt-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-yellow-500/10">
                      <AlertTriangle className="w-6 h-6 text-yellow-400" />
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs">Exposure</p>
                      <p className="text-xl font-bold text-white">
                        {user.exposure?.toLocaleString()} G$
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Position count */}
              <Card className="border-slate-800 bg-slate-900/50">
                <CardContent className="p-4 pt-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-violet-500/10">
                            <Target className="w-6 h-6 text-violet-400" />
                        </div>
                        <div>
                            <p className="text-slate-400 text-xs">Positions</p>
                            <p className="text-xl font-bold text-white">
                                {user.positions?.length || 0}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            </div>

            {/* Position List */}
            <Card className="border-slate-800 bg-slate-900/50">
              <CardContent>
                {user.positions?.length > 0 ? (() => {
  const openPositions = user.positions.filter(p => p.open);
  const closedPositions = user.positions.filter(p => !p.open);

  return (
    <>

      {/* OPEN POSITIONS */}
      <div className="flex items-center justify-between mb-2">
        <CardTitle className="text-white pt-6">Open Positions</CardTitle>
        <button
          onClick={() => setOpenSection(!openSection)}
          className="text-slate-400 text-sm underline"
        >
          {openSection ? "Hide" : `Show (${openPositions.length})`}
        </button>
      </div>
      {openSection && (
        <>
          {/* Always show header, flex for small screens, grid for md+ */}
          <div className="flex md:hidden justify-between pr-2 text-slate-500 text-sm mb-2">
            <span className="font-medium  ml-[10px]">Market</span>
            <span className="w-[100px] text-right">Profit / Loss</span>
          </div>
          <div className="hidden md:grid grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)] items-center pr-4 text-slate-500 text-sm mb-2">
            <span className="justify-self-start ml-[10px]">Market</span>
            <span className="justify-self-end">Buy Price</span>
            <span className="justify-self-end">Current Price</span>
            <span className="justify-self-end">Profit / Loss</span>
          </div>
        </>
      )}

      {openSection && (
        <div className="space-y-4 mb-6">
          {openPositions.map((position) => (
            <Link key={`${position.poll_id}-${position.side}-${position.position_id ?? position.timestamp}`} to={`/EventDetail?id=${position.poll_id}`}>
            <div
              className="p-4 rounded-lg border border-slate-800 bg-slate-800/50 hover:bg-slate-700 transition-all"
            >
              {/* Small screen: flex row, md+: grid */}
              <div className="flex flex-col md:grid md:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)] md:items-center md:gap-4">
                {/* Small screen: flex row with title and PnL side by side */}
                <div className="flex flex-row md:block w-full md:col-span-1">
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium mb-2 md:mb-2 truncate">{position.poll_title}</p>
                    <div className="flex items-center gap-3 mb-1">
                      <Badge
                        className={`flex items-center justify-center ${
                          position.side === "Yes"
                            ? "!bg-emerald-500/10 !text-emerald-400"
                            : "bg-red-500/10 text-red-400 border-red-500/30"
                        }`}
                      >
                        {position.side.toUpperCase()}
                      </Badge>
                      <span className="text-slate-400 text-sm whitespace-normal md:whitespace-nowrap">
                        @ {position.avg_price} G$
                      </span>
                    </div>
                  </div>
                  {/* Small screen PnL - right-aligned, stacked */}
                  <div className="flex flex-col items-end md:hidden ml-2 min-w-[100px] justify-end">
                    <span
                      className={`font-bold ${
                        position.current_pnl >= 0
                          ? "text-emerald-400"
                          : "text-red-400"
                      }`}
                    >
                      {position.current_pnl >= 0 ? "+" : ""}
                      {position.current_pnl} G$
                    </span>
                    <span
                      className={`text-sm ${
                        position.current_pnl >= 0
                          ? "text-emerald-400"
                          : "text-red-400"
                      }`}
                    >
                      ({(position.pct_change * 100).toFixed(1)}%)
                    </span>
                  </div>
                </div>
                {/* md+ grid: buy price, current price, PnL */}
                <span className="hidden md:inline-block text-slate-300 text-sm justify-self-end">{position.avg_price} G$</span>
                <span className="hidden md:inline-block text-slate-300 text-sm justify-self-end">{position.current_price / 100} G$</span>
                <div className="hidden md:flex text-right flex-col items-end justify-self-end">
                  <span
                    className={`font-bold ${
                      position.current_pnl >= 0
                        ? "text-emerald-400"
                        : "text-red-400"
                    }`}
                  >
                    {position.current_pnl >= 0 ? "+" : ""}
                    {position.current_pnl} G$
                  </span>
                  <span
                    className={`text-sm ${
                      position.current_pnl >= 0
                        ? "text-emerald-400"
                        : "text-red-400"
                    }`}
                  >
                    ({(position.pct_change * 100).toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
            </Link>
          ))}
        </div>
      )}

      {/* CLOSED POSITIONS */}
      <div className="flex items-center justify-between mt-4 mb-2">
        <CardTitle className="text-white">Closed Positions</CardTitle>
        <button
          onClick={() => setClosedSection(!closedSection)}
          className="text-slate-400 text-sm underline"
        >
          {closedSection ? "Hide" : `Show (${closedPositions.length})`}
        </button>
      </div>
      {closedSection && (
        <>
          {/* Always show header, flex for small screens, grid for md+ */}
          <div className="flex md:hidden justify-between pr-2 text-slate-500 text-sm mb-2">
            <span className="font-medium  ml-[10px]">Market</span>
            <span className="w-[100px] text-right">Profit / Loss</span>
          </div>
          <div className="hidden md:grid grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)] items-center pr-4 text-slate-500 text-sm mb-2">
            <span className="justify-self-start  ml-[10px]">Market</span>
            <span className="justify-self-end">Buy Price</span>
            <span className="justify-self-end">Final Price</span>
            <span className="justify-self-end">Profit / Loss</span>
          </div>
        </>
      )}

      {closedSection && (
        <div className="space-y-4">
          {closedPositions.map((position) => (
            <Link key={`${position.poll_id}-${position.side}-${position.position_id ?? position.timestamp}`} to={`/EventDetail?id=${position.poll_id}`}>
            <div
              className="p-4 rounded-lg border border-slate-800 bg-slate-800/50 hover:bg-slate-700 transition-all"
            >
              {/* Small screen: flex row, md+: grid */}
              <div className="flex flex-col md:grid md:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)] md:items-center md:gap-4">
                {/* Small screen: flex row with title and PnL side by side */}
                <div className="flex flex-row md:block w-full md:col-span-1">
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium mb-2 md:mb-2 truncate">{position.poll_title}</p>
                    <div className="flex items-center gap-3 mb-1">
                      <Badge
                        className={`flex items-center justify-center ${
                          position.side === "Yes"
                            ? "!bg-emerald-500/10 !text-emerald-400"
                            : "bg-red-500/10 text-red-400 border-red-500/30"
                        }`}
                      >
                        {position.side.toUpperCase()}
                      </Badge>
                      <span className="text-slate-400 text-sm whitespace-normal md:whitespace-nowrap">
                        @ {position.avg_price} G$
                      </span>
                    </div>
                  </div>
                  {/* Small screen PnL - right-aligned, stacked */}
                  <div className="flex flex-col items-end md:hidden ml-2 min-w-[100px] justify-end">
                    <span
                      className={`font-bold ${
                        position.current_pnl >= 0
                          ? "text-emerald-400"
                          : "text-red-400"
                      }`}
                    >
                      {position.current_pnl >= 0 ? "+" : ""}
                      {position.current_pnl} G$
                    </span>
                    <span
                      className={`text-sm ${
                        position.current_pnl >= 0
                          ? "text-emerald-400"
                          : "text-red-400"
                      }`}
                    >
                      ({(position.pct_change * 100).toFixed(1)}%)
                    </span>
                  </div>
                </div>
                {/* md+ grid: buy price, final price, PnL */}
                <span className="hidden md:inline-block text-slate-300 text-sm justify-self-end">{position.avg_price} G$</span>
                <span className="hidden md:inline-block text-slate-300 text-sm justify-self-end">{position.current_price / 100} G$</span>
                <div className="hidden md:flex text-right flex-col items-end justify-self-end">
                  <span
                    className={`font-bold ${
                      position.current_pnl >= 0
                        ? "text-emerald-400"
                        : "text-red-400"
                    }`}
                  >
                    {position.current_pnl >= 0 ? "+" : ""}
                    {position.current_pnl} G$
                  </span>
                  <span
                    className={`text-sm ${
                      position.current_pnl >= 0
                        ? "text-emerald-400"
                        : "text-red-400"
                    }`}
                  >
                    ({(position.pct_change * 100).toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
            </Link>
          ))}
        </div>
      )}

    </>
  );
})() : (
  <div className="text-center py-12">
    <Target className="w-12 h-12 text-slate-600 mx-auto mb-4" />
    <p className="text-slate-400">No positions found</p>
  </div>
)}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}