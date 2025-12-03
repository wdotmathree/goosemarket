import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Clock, TrendingUp, Users, DollarSign } from "lucide-react";
import { format } from "date-fns";
import { createPageUrl } from "@/utils";
import { useAuth } from "@/context/AuthContext";

export default function EventDetail() {
	const navigate = useNavigate();
	const queryClient = useQueryClient();
	const { username, setBalance } = useAuth();
	const [betAmount, setBetAmount] = useState("");
	const [selectedSide, setSelectedSide] = useState(null);
	const [error, setError] = useState(null);
	const [isBuy, setIsBuy] = useState(true);
	const [position, setPosition] = useState([]);
	const { userId, isAdmin } = useAuth();

	const [pollStats, setPollStats] = useState({ num_traders: 0, volume: 0, "24h_volume": 0 });

	const urlParams = new URLSearchParams(window.location.search);
	const eventId = urlParams.get("id"); // now defined first

	const fetchPollStats = async () => {
	if (!eventId) return;
	try {
		const res = await fetch(`/api/polls/${eventId}/stats`);
		if (!res.ok) throw new Error("Failed to fetch poll stats");
		const data = await res.json();
		setPollStats(data);
	} catch (err) {
		console.error(err);
	}
	};

	useEffect(() => {
	fetchPollStats();
	}, [eventId]);

	// Preselect outcome button based on event.outcome

	// Get user_id from cookie
	const getUserId = () => {
		const cookie = document.cookie.split("user-info=")[1]?.split(";")[0];
		if (!cookie) return null;
		try {
			const userInfo = JSON.parse(atob(cookie));
			return userInfo.user_id;
		} catch {
			return null;
		}
	};

	// Mutation for placing bet
	const placeBetMutation = useMutation({
		mutationFn: async ({ pollId, outcome, numShares, buy }) => {
			const userId = getUserId();
			if (!userId) throw new Error("User not logged in");

			const res = await fetch(buy ? "/api/trades/buy" : "/api/trades/sell", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					poll_id: pollId,
					user_id: userId,
					outcome: outcome,
					num_shares: numShares,
					buy: buy,
				}),
			});

			if (!res.ok) {
				const error = await res.json();
				throw new Error(error.error || "Failed to place bet");
			}

			return res.json();
		},
		onSuccess: (data, variables) => {
			const { buy } = variables
			if (buy){
				setBalance(prev => prev - 100*data.cost)
			} else{
				setBalance(prev => prev + 100*data.payout)
			}
			// Refresh poll data to show updated prices
			queryClient.invalidateQueries(["poll", eventId]);
			// Reset form
			fetchPollStats();
			fetchPosition();
			setBetAmount("");
			setSelectedSide(null);
			setError(null);
		},
		onError: (error) => {
			setError(error.message);
		},
	});
	const { data: event, isLoading } = useQuery({
		queryKey: ["poll", eventId],
		queryFn: async () => {
			if (!eventId) return null;

			// Fetch the poll data
			const pollRes = await fetch(`/api/polls/${eventId}`);
			if (!pollRes.ok) throw new Error("Failed to load poll");
			const pollData = await pollRes.json();

			// Fetch the price data
			const priceRes = await fetch(`/api/polls/${eventId}/price`);
			if (!priceRes.ok) throw new Error("Failed to load price");
			const priceData = await priceRes.json();

			// Combine the data
			return {
				...pollData.poll,
				yes_shares: priceData.q_yes,
				no_shares: priceData.q_no,
				total_shares: priceData.q_yes + priceData.q_no,
				price_yes: priceData.price_yes,
				price_no: priceData.price_no,
			};
		},
		enabled: !!eventId,
	});

	const handlePlaceBet = () => {
		if (!betAmount || parseFloat(betAmount) <= 0) {
			setError("Please enter a valid bet amount");
			return;
		}
		if (!selectedSide) {
			setError("Please select YES or NO");
			return;
		}

		placeBetMutation.mutate({
			pollId: parseInt(eventId),
			outcome: selectedSide.toUpperCase(),
			numShares: parseInt(betAmount),
			buy: isBuy,
		});
	};

	const estimateQuery = useQuery({
		queryKey: ["estimate", eventId, selectedSide, betAmount],
		queryFn: async () => {
			if (!selectedSide || !betAmount || parseInt(betAmount) <= 0) return 0;

			const res = await fetch(`/api/polls/${eventId}/estimate`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					outcome_yes: selectedSide === "yes",
					num_shares: parseInt(betAmount),
					buy: isBuy
				}),
			});

			if (!res.ok) throw new Error("Failed to estimate cost");

			const data = await res.json();
			return data.estimate;
		},
		enabled: !!eventId && !!selectedSide && !!betAmount,
	});

	useEffect(() => {
		fetchPosition();
	}, [eventId, userId]);

	const fetchPosition = async () => {
		if (!eventId || !userId) return;
		try {
			const res = await fetch("/api/positions", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					user_id: userId,
					poll_id: parseInt(eventId)
				}),
			});
			if (!res.ok) throw new Error("Failed to fetch position");
			const data = await res.json();
			// Expect data.positions to be an array
			setPosition(Array.isArray(data.positions) ? data.positions : []);
		} catch (err) {
			console.error(err);
		}
	};

	useEffect(() => {
		const setSide = async () => {
			if (!event) return;
			try{
				setSelectedSide(event.outcome === true ? "yes" : event.outcome === false ? "no" : null)
			} catch (err) {
			console.error(err);
			}
		};
		setSide()
	}, [event]);

	if (isLoading) {
		return (
			<div className="min-h-screen bg-slate-950 flex items-center justify-center">
				<div className="text-center">
					<h2 className="text-2xl font-bold text-white mb-4">Loading...</h2>
				</div>
			</div>
		);
	}

	if (!event) {
		return (
			<div className="min-h-screen bg-slate-950 flex items-center justify-center">
				<div className="text-center">
					<h2 className="text-2xl font-bold text-white mb-4">Event not found</h2>
					<Button onClick={() => navigate(createPageUrl("Dashboard"))}>Back to Dashboard</Button>
				</div>
			</div>
		);
	}

	const categoryColors = {
		Academics: "bg-blue-500/10 text-blue-400 border-blue-500/20",
		Sports: "bg-orange-500/10 text-orange-400 border-orange-500/20",
		"Campus Life": "bg-purple-500/10 text-purple-400 border-purple-500/20",
		Politics: "bg-red-500/10 text-red-400 border-red-500/20",
		Weather: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
		Other: "bg-slate-500/10 text-slate-400 border-slate-500/20",
	};

	const getPercent = (value) => {
		if (value === null || value === undefined) return 50;
		// API returns ints (0-100). If we ever get 0-1 floats, scale up.
		if (value >= 1) return Math.round(value);
		return Math.round(value * 100);
	};
	const yesPercent = getPercent(event?.price_yes);
	const noPercent = Math.max(0, 100 - yesPercent);

	return (
		<div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
			<div className="max-w-5xl mx-auto px-6 py-8">
				{/* Back Button */}
				<Button
					variant="ghost"
					onClick={() => navigate(createPageUrl("Dashboard"))}
					className="mb-6 text-slate-300 hover:text-emerald-400 hover:bg-slate-800/60 transition-colors"
				>
					<ArrowLeft className="w-4 h-4 mr-2" />
					Back to Markets
				</Button>

				<div className="grid lg:grid-cols-3 gap-6">
					{/* Main Content */}
					<div className="lg:col-span-2 space-y-6">
						{/* Event Header */}
						<Card className="border-slate-800 bg-slate-900/50">
							<CardHeader>
								<div className="flex items-start justify-between mb-4">
									{!event.has_ended ? (
										<Badge
											variant="outline"
											className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 border"
										>
											Open
										</Badge>
									) : null}
									{event.ends_at && (
										<div className="flex items-center gap-2 text-slate-400">
											<Clock className="w-4 h-4" />
											<span className="text-sm">
												{event.has_ended ? "Closed" : "Closes"}{" "}
												{format(new Date(event.ends_at), "MMM d, yyyy 'at' h:mm a")}
											</span>
										</div>
									)}
								</div>
								<div className="flex flex-wrap gap-2 mt-2">
								  {event.has_ended && <Badge variant="outline" className="bg-slate-500/10 text-slate-400 border-slate-500/20 border">Closed</Badge>}
								  {event.tags?.filter(tag => tag !== "Closed").map((tag) => (
								    <Badge key={tag} variant="outline" className="bg-slate-500/10 text-slate-400 border-slate-500/20 border">
								      {tag}
								    </Badge>
								  ))}
								</div>
								<CardTitle className="text-3xl font-bold text-white leading-tight">{event.title}</CardTitle>
							</CardHeader>
							<CardContent>
								<p className="text-slate-300 leading-relaxed">
									{event.description || "No additional description provided for this market."}
								</p>
							</CardContent>
						</Card>

						{/* Betting Interface */}
						<Card className="border-slate-800 bg-slate-900/50">
							<div className="flex mb-4">
								<button
									onClick={() => {
										setIsBuy(true);
										setBetAmount("");
									}}
									className={`flex-1 text-center py-2 text-white ${
										isBuy ? "border-b-2 border-white" : "opacity-60"
									}`}
									disabled={event.has_ended}
								>
									Buy
								</button>
								<button
									onClick={() => {
										setIsBuy(false);
										setBetAmount("");
									}}
									className={`flex-1 text-center py-2 text-white ${
										!isBuy ? "border-b-2 border-white" : "opacity-60"
									}`}
									disabled={event.has_ended}
								>
									Sell
								</button>
							</div>
							<CardHeader className="pt-0">
								<CardTitle className="text-white">Place Your Bet</CardTitle>
							</CardHeader>
							<CardContent className="space-y-4">
								<div className="grid grid-cols-2 gap-4">
									<Button
									onClick={() => setSelectedSide("yes")}
									variant="ghost"
									className={`h-24 text-lg font-semibold transition-all ${
										selectedSide === "yes"
											? "bg-emerald-600 hover:bg-emerald-500 text-white border-2 border-emerald-400"
											: "bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30"
									} ${event.has_ended ? "opacity-50 cursor-not-allowed hover:bg-none" : ""}`}
									disabled={event.has_ended}
								>
										<div className="flex items-center gap-2">
											<span>{isBuy ? "Buy Yes" : "Sell Yes"}</span>
											<span className="text-2xl">
												{yesPercent}%
											</span>
										</div>
									</Button>
									<Button
									onClick={() => setSelectedSide("no")}
									variant="ghost"
									className={`h-24 text-lg font-semibold transition-all ${
										selectedSide === "no"
											? "bg-red-600 hover:bg-red-500 text-white border-2 border-red-400"
											: "bg-red-500/15 hover:bg-red-500/25 text-red-300 border border-red-500/30"
									} ${event.has_ended ? "opacity-50 cursor-not-allowed hover:bg-none" : ""}`}
									disabled={event.has_ended}
								>
										<div className="flex items-center gap-2">
											<span>{isBuy ? "Buy No" : "Sell No"}</span>
											<span className="text-2xl">
												{noPercent}%
											</span>
										</div>
									</Button>
								</div>

								{selectedSide && (
									<div className="space-y-4 p-4 rounded-lg bg-slate-800/50 border border-slate-700">
										{error && (
											<div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
												{error}
											</div>
										)}
										<div>
											<label className="text-sm text-slate-400 mb-2 block">Amount (Shares)</label>
											<Input
												type="number"
												placeholder="Enter number of shares..."
												value={betAmount}
												onChange={(e) => setBetAmount(e.target.value)}
												className="bg-slate-900 border-slate-700 text-white"
											/>
										</div>
										<div className="flex items-center justify-between text-sm">
											<span className="text-slate-400">{isBuy ? "Estimated Cost:" : "Estimated Gain:"}</span>
											<span className={`${isBuy ? "text-red-400" : "text-emerald-400"} font-semibold`}>
												{estimateQuery.isFetching
													? "..."
													: estimateQuery.data
														? `~${Number(estimateQuery.data).toFixed(2)} G$`
														: "0 G$"}
											</span>
										</div>
										<Button
											onClick={handlePlaceBet}
											className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold"
											disabled={!betAmount || parseFloat(betAmount) <= 0 || placeBetMutation.isPending || event.has_ended}
										>
											{placeBetMutation.isPending ? (isBuy ? "Placing Buy..." : "Placing Sell...") : (isBuy ? "Place Buy" : "Place Sell")}
										</Button>
									</div>
								)}
							</CardContent>
						</Card>

						{/* Pool Distribution */}
						<Card className="border-slate-800 bg-slate-900/50">
							<CardHeader>
								<CardTitle className="text-white">Market Distribution</CardTitle>
							</CardHeader>
							<CardContent className="space-y-4">
								<div>
									<div className="flex justify-between text-sm mb-2">
										<span className="text-emerald-400 font-semibold">
											YES{" "}
											{yesPercent}
											%
										</span>
										<span className="text-red-400 font-semibold">
											NO{" "}
											{noPercent}
											%
										</span>
									</div>
									<div className="relative h-3 bg-slate-800 rounded-full overflow-hidden">
										<div
											className="absolute left-0 top-0 h-full bg-emerald-500 transition-all duration-500"
											style={{
												width: `${yesPercent}%`,
											}}
										/>
										<div
											className="absolute right-0 top-0 h-full bg-red-500 transition-all duration-500"
											style={{
												width: `${noPercent}%`,
											}}
										/>
									</div>
								</div>
							</CardContent>
						</Card>
					</div>

					{/* Sidebar */}
					<div className="space-y-6">
						{/* Stats Card */}
						<Card className="border-slate-800 bg-slate-900/50">
							<CardHeader>
								<CardTitle className="text-white">Market Stats</CardTitle>
							</CardHeader>
							<CardContent className="space-y-4">
								<div className="flex items-center justify-between">
									<div className="flex items-center gap-2 text-slate-400">
										<DollarSign className="w-4 h-4" />
										<span className="text-sm">Total Pool</span>
									</div>
									<span className="text-white font-semibold">{(pollStats.volume/100).toFixed(2).toLocaleString()} G$</span>
								</div>
								<div className="flex items-center justify-between">
									<div className="flex items-center gap-2 text-slate-400">
										<Users className="w-4 h-4" />
										<span className="text-sm">Traders</span>
									</div>
									<span className="text-white font-semibold">{pollStats.num_traders.toLocaleString()}</span>
								</div>
								<div className="flex items-center justify-between">
									<div className="flex items-center gap-2 text-slate-400">
										<TrendingUp className="w-4 h-4" />
										<span className="text-sm">24h Volume</span>
									</div>
									<span className="text-white font-semibold">{(pollStats["24h_volume"]/100).toFixed(2).toLocaleString()} G$</span>
								</div>
							</CardContent>
						</Card>

					{/* Your Position */}
					<Card className="border-slate-800 bg-slate-900/50">
					  <CardHeader>
					    <CardTitle className="text-white">Your Position</CardTitle>
					  </CardHeader>
					  <CardContent>
					    {position && position.length > 0 ? (
					      position.map((pos) => (
					        <div key={pos.side} className="space-y-2 mb-4 p-2 border-b border-slate-700 last:border-b-0">
					          <div className="flex justify-between text-sm text-slate-400">
					            <span>Side:</span>
					            <span className="text-white font-semibold">{pos.side}</span>
					          </div>
					          <div className="flex justify-between text-sm text-slate-400">
					            <span>Quantity:</span>
					            <span className="text-white font-semibold">{pos.quantity}</span>
					          </div>
					          <div className="flex justify-between text-sm text-slate-400">
					            <span>Price Purchased:</span>
					            <span className="text-white font-semibold">{pos.avg_price.toFixed(2)} G$</span>
					          </div>
					          <div className="flex justify-between text-sm text-slate-400">
					            <span>Current Price:</span>
					            <span className="text-white font-semibold">{(pos.current_price/100).toFixed(2)} G$</span>
					          </div>
					          <div className="flex justify-between text-sm text-slate-400">
					            <span>PnL:</span>
					            <span className={`font-semibold ${pos.current_pnl >= 0 ? "text-emerald-400" : "text-red-400"}`}>
					              {pos.current_pnl.toFixed(2)} G$
					            </span>
					          </div>
					        </div>
					      ))
					    ) : (
					      <div className="text-center py-8">
					        <p className="text-slate-400 text-sm mb-2">No active bets</p>
					        <p className="text-slate-500 text-xs">Place a bet to see your position</p>
					      </div>
					    )}
					  </CardContent>
					</Card>
					{isAdmin && !event.has_ended && (
					  <Button
					    className="w-full mt-4 bg-red-500 hover:bg-red-600 text-white font-semibold"
					    onClick={async () => {
					      try {
					        const res = await fetch("/api/admin/update", {
					          method: "POST",
					          headers: { "Content-Type": "application/json" },
					          body: JSON.stringify({
					            poll_id: parseInt(eventId),
					            ends_at: new Date().toISOString()
					          }),
					        });
					        if (!res.ok) throw new Error("Failed to end poll");

					        // Disable betting interface
					        event.has_ended = true;
					      } catch (err) {
					        console.error(err);
					      }
					    }}
					  >
					    End Poll
					  </Button>
					)}
					</div>
				</div>
			</div>
		</div>
	);
}
