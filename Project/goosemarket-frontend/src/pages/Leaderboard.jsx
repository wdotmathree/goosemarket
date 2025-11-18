import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trophy, Medal, Award, TrendingUp } from "lucide-react";

const mockLeaderboard = [
  { rank: 1, username: "alex_uwat", faculty: "Engineering", balance: 15420, change: "+12.5%" },
  { rank: 2, username: "sarah_math", faculty: "Mathematics", balance: 14280, change: "+8.3%" },
  { rank: 3, username: "mike_cs", faculty: "Computer Science", balance: 12950, change: "+15.2%" },
  { rank: 4, username: "emma_ahs", faculty: "Applied Health", balance: 11800, change: "+6.7%" },
  { rank: 5, username: "david_eng", faculty: "Engineering", balance: 10990, change: "+9.1%" },
  { rank: 6, username: "lisa_arts", faculty: "Arts", balance: 9840, change: "+4.2%" },
  { rank: 7, username: "james_sci", faculty: "Science", balance: 8920, change: "-2.3%" },
  { rank: 8, username: "olivia_env", faculty: "Environment", balance: 8450, change: "+7.8%" },
  { rank: 9, username: "ryan_math", faculty: "Mathematics", balance: 7890, change: "+11.4%" },
  { rank: 10, username: "sophia_cs", faculty: "Computer Science", balance: 7320, change: "+3.9%" }
];

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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <span className="text-3xl">👑</span>
                <div>
                  <p className="text-slate-400 text-sm">Top Trader</p>
                  <p className="text-xl font-bold text-white">{mockLeaderboard[0].username}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <TrendingUp className="w-8 h-8 text-emerald-400" />
                <div>
                  <p className="text-slate-400 text-sm">Highest Gain</p>
                  <p className="text-xl font-bold text-emerald-400">+15.2%</p>
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
                  <p className="text-xl font-bold text-white">487</p>
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
              {mockLeaderboard.map((entry) => (
                <div
                  key={entry.rank}
                  className={`p-4 rounded-lg border transition-all hover:scale-[1.02] ${getRankBg(entry.rank)}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {/* Rank */}
                      <div className="w-12 flex items-center justify-center">
                        {getRankIcon(entry.rank)}
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
                      <Badge
                        variant="outline"
                        className={`${
                          entry.change.startsWith('+')
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : 'bg-red-500/10 text-red-400 border-red-500/30'
                        }`}
                      >
                        {entry.change}
                      </Badge>
                      <div className="text-right">
                        <p className="text-white font-bold text-lg">
                          {entry.balance.toLocaleString()} G$
                        </p>
                        <p className="text-slate-400 text-xs">Balance</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Your Rank Card */}
        <Card className="mt-6 border-slate-800 bg-gradient-to-r from-slate-900/50 to-violet-900/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white font-semibold">
                  AC
                </div>
                <div>
                  <p className="text-white font-semibold">Your Rank</p>
                  <p className="text-slate-400 text-sm">Keep trading to climb higher!</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-4xl font-bold text-white">#42</p>
                <p className="text-slate-400 text-sm">1,250 G$</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}