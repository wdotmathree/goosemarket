import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, TrendingUp, Flame } from "lucide-react";
import EventCard from "../components/market/EventCard";
import { Skeleton } from "@/components/ui/skeleton";

export default function Dashboard() {
	const [searchQuery, setSearchQuery] = useState("");
	const [categoryFilter, setCategoryFilter] = useState("all");

	// Load polls from the API
	const { data: events = [], isLoading } = useQuery({
		queryKey: ["polls"],
		queryFn: async () => {
			const res = await fetch("/api/polls");
			if (!res.ok) throw new Error("Failed to load polls");
			const json = await res.json();
			// Fetch price data for each poll
			const pollsWithPrices = await Promise.all(
				(json.polls || []).map(async (poll) => {
					try {
						const priceRes = await fetch(`/api/polls/${poll.id}/price`);
						if (priceRes.ok) {
							const priceData = await priceRes.json();
							return {
								...poll,
								yes_votes: priceData.q_yes,
								no_votes: priceData.q_no,
								total_votes: priceData.q_yes + priceData.q_no,
							};
						}
					} catch (e) {
						console.error(`Failed to fetch price for poll ${poll.id}:`, e);
					}
					return {
						...poll,
						yes_percentage: 50,
						no_percentage: 50,
						total_pool: 100,
					};
				})
			);
			return pollsWithPrices;
		},
	});

	// Apply filters (search + category + active only)
	const filteredEvents = events.filter((event) => {
		const matchesSearch = event.title?.toLowerCase().includes(searchQuery.toLowerCase());
		// const matchesCategory = categoryFilter === "all" || event.category === categoryFilter;
		return matchesSearch;
	});

	return (
		<div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
			<div className="max-w-7xl mx-auto px-6 py-8">
				{/* Hero Section */}
				<div className="mb-12">
					<div className="flex items-center gap-3 mb-4">
						<div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-violet-500/20">
							<Flame className="w-6 h-6 text-emerald-400" />
						</div>
						<h1 className="text-4xl font-bold text-white">Trending Markets</h1>
					</div>
					<p className="text-slate-400 text-lg">
						Trade on UWaterloo events with Goose Dollars. No real money, just campus predictions.
					</p>
				</div>

				{/* Filters */}
				<div className="flex flex-col sm:flex-row gap-4 mb-8">
					<div className="relative flex-1">
						<Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
						<Input
							type="text"
							placeholder="Search markets..."
							value={searchQuery}
							onChange={(e) => setSearchQuery(e.target.value)}
							className="pl-11 bg-slate-900 border-slate-800 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-emerald-500/50"
						/>
					</div>
					<Select value={categoryFilter} onValueChange={setCategoryFilter}>
						<SelectTrigger className="w-full sm:w-48 bg-slate-900 border-slate-800 text-white">
							<SelectValue placeholder="All Categories" />
						</SelectTrigger>
						<SelectContent className="bg-slate-900 border-slate-800">
							<SelectItem value="all">All Categories</SelectItem>
							<SelectItem value="Academics">Academics</SelectItem>
							<SelectItem value="Sports">Sports</SelectItem>
							<SelectItem value="Campus Life">Campus Life</SelectItem>
							<SelectItem value="Politics">Politics</SelectItem>
							<SelectItem value="Weather">Weather</SelectItem>
							<SelectItem value="Other">Other</SelectItem>
						</SelectContent>
					</Select>
				</div>

				{/* Stats Banner */}
				<div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
					<div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800">
						<div className="flex items-center gap-3">
							<TrendingUp className="w-8 h-8 text-emerald-400" />
							<div>
								<p className="text-slate-400 text-sm">Active Markets</p>
								<p className="text-2xl font-bold text-white">{filteredEvents.length}</p>
							</div>
						</div>
					</div>
					<div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800">
						<div className="flex items-center gap-3">
							<span className="text-3xl">📊</span>
							<div>
								<p className="text-slate-400 text-sm">Total Volume</p>
								<p className="text-2xl font-bold text-white">
									{events.reduce((sum, e) => sum + (Number(e.total_pool) || 0), 0).toLocaleString()} G$
								</p>
							</div>
						</div>
					</div>
					<div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800">
						<div className="flex items-center gap-3">
							<span className="text-3xl">👥</span>
							<div>
								<p className="text-slate-400 text-sm">Active Traders</p>
								<p className="text-2xl font-bold text-white">{Math.floor(Math.random() * 500 + 200)}</p>
							</div>
						</div>
					</div>
				</div>

				{/* Events Grid */}
				{isLoading ? (
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						{[...Array(6)].map((_, i) => (
							<div key={i} className="p-6 rounded-xl bg-slate-900/50 border border-slate-800">
								<Skeleton className="h-6 w-24 mb-4 bg-slate-800" />
								<Skeleton className="h-16 w-full mb-4 bg-slate-800" />
								<div className="grid grid-cols-2 gap-3">
									<Skeleton className="h-20 bg-slate-800" />
									<Skeleton className="h-20 bg-slate-800" />
								</div>
							</div>
						))}
					</div>
				) : filteredEvents.length === 0 ? (
					<div className="text-center py-20">
						<div className="w-20 h-20 mx-auto mb-4 rounded-full bg-slate-900 flex items-center justify-center">
							<Search className="w-10 h-10 text-slate-600" />
						</div>
						<h3 className="text-xl font-semibold text-slate-400 mb-2">No markets found</h3>
						<p className="text-slate-500">Try adjusting your filters or search query</p>
					</div>
				) : (
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						{filteredEvents.map((event) => (
							<EventCard key={event.id} event={event} />
						))}
					</div>
				)}
			</div>
		</div>
	);
}
