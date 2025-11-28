import React from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, Clock, DollarSign } from "lucide-react";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";
import { createPageUrl } from "@/utils";

const categoryColors = {
  "Academics": "bg-blue-500/10 text-blue-400 border-blue-500/20",
  "Sports": "bg-orange-500/10 text-orange-400 border-orange-500/20",
  "Campus Life": "bg-purple-500/10 text-purple-400 border-purple-500/20",
  "Politics": "bg-red-500/10 text-red-400 border-red-500/20",
  "Weather": "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  "Other": "bg-slate-500/10 text-slate-400 border-slate-500/20"
};

export default function EventCard({ event, pollStats }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(createPageUrl(`EventDetail?id=${event.id}`));
  };

  return (
		<Card
			onClick={handleClick}
			className="group relative overflow-hidden border-slate-800 bg-slate-900/50 backdrop-blur-sm hover:bg-slate-900 transition-all duration-300 cursor-pointer hover:shadow-xl hover:shadow-emerald-500/5 hover:-translate-y-1"
		>
			{/* Gradient overlay on hover */}
			<div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-violet-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

			<div className="relative p-5 space-y-4">
				{/* Header */}
				<div className="flex items-start justify-between gap-3">
					<div className="flex gap-2 mt-2 max-w-[75%] overflow-x-auto overflow-y-hidden whitespace-nowrap -ms-overflow-style-none scrollbar-hide">
						{event.has_ended && <Badge variant="outline" className="inline-block bg-slate-500/10 text-slate-400 border-slate-500/20 border">Closed</Badge>}
						{event.tags?.filter(tag => tag !== "Closed").map((tag) => (
						<Badge key={tag} variant="outline" className="inline-block bg-slate-500/10 text-slate-400 border-slate-500/20 border">
							{tag}
						</Badge>
						))}
					</div>
					{event.ends_at && (
						<div className="flex items-center gap-1 text-xs text-slate-400">
							<Clock className="w-3 h-3" />
							<span>{format(new Date(event.ends_at), "MMM d")}</span>
						</div>
					)}
				</div>

				{/* Title */}
				<h3 className="text-lg font-semibold text-white leading-tight line-clamp-2 group-hover:text-emerald-400 transition-colors">
					{event.title}
				</h3>

				{/* Betting Options */}
				<div className="grid grid-cols-2 gap-3">
					<Button
						onClick={(e) => {
							e.stopPropagation();
							handleClick();
						}}
						className="relative overflow-hidden bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:border-emerald-500/50 transition-all"
					>
						<div className="flex items-center gap-2">
							<span>Yes:</span>
							<span className="text-2xl">
								{event.total_votes != 0 ? Math.round((event.yes_votes / event.total_votes) * 100) : 50}%
							</span>
						</div>
					</Button>
					<Button
						onClick={(e) => {
							e.stopPropagation();
							handleClick();
						}}
						className="relative overflow-hidden bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 hover:border-red-500/50 transition-all"
					>
						<div className="flex items-center gap-2">
							<span>No:</span>
							<span className="text-2xl">
								{event.total_votes != 0 ? Math.round((event.no_votes / event.total_votes) * 100): 50}%
							</span>
						</div>
					</Button>
				</div>

				{/* Footer Stats */}
				<div className="flex items-center justify-between pt-3 border-t border-slate-800">
					<div className="flex items-center gap-2 text-slate-400">
						<TrendingUp className="w-4 h-4" />
						<span className="text-xs">{pollStats?.num_traders?.toLocaleString() || 0} traders</span>
					</div>
					<div className="flex items-center gap-1 text-emerald-400 font-semibold">
						<span className="text-sm">{((pollStats?.volume ?? 0) / 100).toFixed(2).toLocaleString()} G$</span>
					</div>
				</div>
			</div>
		</Card>
  );
}