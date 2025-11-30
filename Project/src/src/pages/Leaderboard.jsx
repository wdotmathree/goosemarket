import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trophy, Medal, Award, TrendingUp } from "lucide-react";

export default function Leaderboard() {
  const getRankIcon = (rank) => {
    if (rank === 1) return <Trophy className="w-6 h-6 text-yellow-400" />;
    if (rank === 2) return <Medal className="w-6 h-6 text-slate-300" />;
    if (rank === 3) return <Award className="w-6 h-6 text-orange-400" />;
    return <span className="text-slate-500 font-semibold">#{rank}</span>;
  };

  const getRankBg = (rank) => {
    if (rank === 1) return "bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border-yellow-500/20";
    if (rank === 2) return "bg-gradient-to-r from-slate-500/10 to-slate-600/10 border-slate-400/20";
    if (rank === 3) return "bg-gradient-to-r from-orange-500/10 to-orange-600/10 border-orange-500/20";
    return "bg-slate-900/50 border-slate-800";
  };

  const [leaders, setLeaders] = useState([]);
  const [userRank, setUserRank] = useState(null);
  const [userCount, setUserCount] = useState(null)
  const [username, setUsername] = useState(null)
  const [userBalance, setUserBalance] = useState(0)

  useEffect(() => {
    async function fetchLeaderboard() {
      try {
        const res = await fetch("/api/leaderboard?$num_users=10", {
          method: "GET",
          headers: { "Content-Type": "application/json" }
        });

        const data = await res.json();
        if (data.top_users) {
          setLeaders(data.top_users);
        }
        if (data.rank !== -1) {
          setUserRank(data.rank);
        }
        if(data.username){
          setUsername(data.username)
        }
        if(data.user_balance){
          setUserBalance(data.user_balance)
        }
      } catch (err) {
        console.error("Failed to fetch leaderboard:", err);
      }
    }

    fetchLeaderboard();

    async function fetchUserCount() {
      try {
        const res = await fetch("/api/leaderboard/count", {
          method: "GET",
          headers: { "Content-Type": "application/json" }
        });
        const data = await res.json();
        if (data.users !== undefined) {
          setUserCount(data.users);
        }
      } catch (err) {
        console.error("Failed to fetch user count:", err);
      }
    }

    fetchUserCount();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-br from-yellow-500/20 to-orange-500/20">
              <Trophy className="w-6 h-6 text-yellow-400" />
            </div>
            <h1 className="text-4xl font-bold text-white">Leaderboard</h1>
          </div>
          <p className="text-slate-400 text-lg">
            Top traders on GooseMarket by total Goose Dollar balance
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <span className="text-3xl">👑</span>
                <div>
                  <p className="text-slate-400 text-sm">Top Trader</p>
                  <p className="text-xl font-bold text-white">{leaders[0]?.username || "..."}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <span className="text-3xl">📊</span>
                <div>
                  <p className="text-slate-400 text-sm">Total Traders</p>
                  <p className="text-xl font-bold text-white">{userCount ?? "..."}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Leaderboard Table */}
        <Card className="border-slate-800 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="text-white">Top 10 Traders</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {leaders.map((entry, i) => {
                const rank = entry.rank || i + 1;
                return (
                  <Link key={rank} to={`/user?id=${entry.id}`}>
                  <div
                    className={`p-4 rounded-lg border transition-all hover:scale-[1.02] ${getRankBg(rank)}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        {/* Rank */}
                        <div className="w-12 flex items-center justify-center">
                          {getRankIcon(rank)}
                        </div>

                        {/* Avatar */}
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white font-semibold">
                          {entry.username.slice(0, 2).toUpperCase()}
                        </div>

                        {/* Info */}
                        <div>
                          <p className="text-white font-semibold">{entry.username}</p>
                          <p className="text-slate-400 text-sm">{entry.faculty}</p>
                        </div>
                      </div>

                      {/* Stats */}
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <p className="text-white font-bold text-lg">
                            {(entry.balance/100).toLocaleString()} G$
                          </p>
                          <p className="text-slate-400 text-xs">Balance</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  </Link>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Your Rank Card */}
        <Card className="mt-6 border-slate-800 bg-gradient-to-r from-slate-500/ to-slate-600/50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white font-semibold">
                    {username?.slice(0, 2).toUpperCase() ?? " "}
                  </div>
                <div>
                  <p className="text-white font-semibold">Your Rank</p>
                  <p className="text-slate-400 text-sm">Keep trading to climb higher!</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-4xl font-bold text-white">{userRank ? "#" + userRank : "…"}</p>
                <p className="text-slate-400 text-sm">{(userBalance/100).toLocaleString()} G$</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}