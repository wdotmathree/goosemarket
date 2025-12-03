import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Shield, Check, X, Clock } from "lucide-react";
import { format } from "date-fns";

export default function Admin() {
  const [pendingEvents, setPendingEvents] = useState([]);
  const [resolveEvents, setResolveEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingEvent, setEditingEvent] = useState(null);
  const [editValues, setEditValues] = useState({
    title: "",
    description: "",
    tags: "",
    ends_at: ""
  });
  const [editingEndedAt, setEditingEndedAt] = useState(null);
  const [newEndedAt, setNewEndedAt] = useState("");
  const handleUpdateEndedAt = async () => {
    try {
      await fetch("/api/admin/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          poll_id: editingEndedAt.id,
          ends_at: new Date(newEndedAt).toISOString()
        })
      });

      setResolveEvents(prev =>
        prev.map(e =>
          e.id === editingEndedAt.id
            ? { ...e, ended_at: newEndedAt }
            : e
        )
      );

      setEditingEndedAt(null);
      setNewEndedAt("");
    } catch (err) {
      console.error("Failed to update ended_at:", err);
    }
  };
  const [viewMode, setViewMode] = useState("review");
  const { incrementBalance } = useAuth();

  useEffect(() => {
    async function fetchAll() {
      try {
        const [reviewRes, resolveRes] = await Promise.all([
          fetch("/api/admin/review/all"),
          fetch("/api/admin/resolve/all")
        ]);

        const reviewData = await reviewRes.json();
        const resolveData = await resolveRes.json();

        if (reviewData.polls) setPendingEvents(reviewData.polls);
        if (resolveData.polls) setResolveEvents(resolveData.polls);
      } catch (err) {
        console.error("Failed to fetch admin data:", err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchAll();
  }, []);

  const handleApprove = async (eventId) => {
    try {
      await fetch("/api/admin/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({"poll_id": eventId})
      });
      setPendingEvents(prev => prev.filter(event => event.id !== eventId));
    } catch (err) {
      console.error("Failed to approve poll:", err);
    }
  };

  const handleReject = async (eventId) => {
    try {
      await fetch("/api/admin/reject", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "poll_id": eventId })
      });
      setPendingEvents(prev => prev.filter(event => event.id !== eventId));
    } catch (err) {
      console.error("Failed to reject poll:", err);
    }
  };

  const openEdit = (event) => {
    setEditingEvent(event);
    setEditValues({
      title: event.title,
      description: event.description || "",
      tags: event.tags?.join(", ") || "",
      ends_at: event.ends_at
    });
  };

  const handleUpdate = async () => {
    try {
      await fetch("/api/admin/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          poll_id: editingEvent.id,
          title: editValues.title,
          description: editValues.description,
          tags: editValues.tags.split(",").map(x => x.trim()).filter(Boolean),
          ends_at: editValues.ends_at ? new Date(editValues.ends_at).toISOString() : null
        })
      });

      // Update UI without refetch
      setPendingEvents(prev =>
        prev.map(e =>
          e.id === editingEvent.id
            ? { ...e, ...editValues, tags: editValues.tags.split(",").map(t => t.trim()) }
            : e
        )
      );

      setEditingEvent(null);
    } catch (err) {
      console.error("Failed to update poll:", err);
    }
  };

  const categoryColors = {
    "Academics": "bg-blue-500/10 text-blue-400 border-blue-500/20",
    "Sports": "bg-orange-500/10 text-orange-400 border-orange-500/20",
    "Campus Life": "bg-purple-500/10 text-purple-400 border-purple-500/20",
    "Politics": "bg-red-500/10 text-red-400 border-red-500/20",
    "Weather": "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    "Other": "bg-slate-500/10 text-slate-400 border-slate-500/20"
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20">
              <Shield className="w-6 h-6 text-violet-400" />
            </div>
            <h1 className="text-4xl font-bold text-white">Admin Panel</h1>
          </div>
          <p className="text-slate-400 text-lg">
            Review and manage pending market submissions
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Clock className="w-8 h-8 text-yellow-400" />
                <div>
                  <p className="text-slate-400 text-sm">Pending Review</p>
                  <p className="text-2xl font-bold text-white">{pendingEvents.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Check className="w-8 h-8 text-emerald-400" />
                <div>
                  <p className="text-slate-400 text-sm">Active Markets</p>
                  <p className="text-2xl font-bold text-white">
                    0
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <span className="text-3xl">📊</span>
                <div>
                  <p className="text-slate-400 text-sm">Total Markets</p>
                  <p className="text-2xl font-bold text-white">{pendingEvents.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Toggle Review vs Resolution */}
        <div className="flex justify-center mb-6">
          <div className="flex border-b border-slate-700 w-full max-w-md justify-around">
            <button
              onClick={() => setViewMode("review")}
              className={`pb-2 px-4 text-white ${
                viewMode === "review" ? "border-b-2 border-white" : "opacity-50"
              }`}
            >
              Pending Review
            </button>
            <button
              onClick={() => setViewMode("resolution")}
              className={`pb-2 px-4 text-white ${
                viewMode === "resolution" ? "border-b-2 border-white" : "opacity-50"
              }`}
            >
              Pending Resolution
            </button>
          </div>
        </div>

        {/* Pending Events */}
        <Card className="border-slate-800 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="text-white">{viewMode === "review" ? "Pending Market Submissions" : "Pending Resolution"}</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto" />
                <p className="text-slate-400 mt-4">Loading submissions...</p>
              </div>
            ) : (viewMode === "review" ? pendingEvents : resolveEvents).length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mx-auto mb-4">
                  <Check className="w-8 h-8 text-slate-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-400 mb-2">All caught up!</h3>
                <p className="text-slate-500">No pending market submissions to review</p>
              </div>
            ) : (
              <div className="space-y-4">
                {(viewMode === "review" ? pendingEvents : resolveEvents).map((event) => (
                  <div
                    key={event.id}
                    className="p-6 rounded-lg border border-slate-800 bg-slate-900/50 hover:bg-slate-900 transition-all"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Badge variant="outline" className="bg-yellow-500/10 text-yellow-400 border-yellow-500/20">
                            Pending Review
                          </Badge>
                          {event.tags && event.tags.map((tag, index) => (
                            <Badge
                              key={index}
                              variant="outline"
                              className={`${categoryColors[tag] || "bg-slate-500/10 text-slate-400 border-slate-500/20"} border`}
                            >
                              {tag}
                            </Badge>
                          ))}
                        </div>
                        <h3 className="text-xl font-semibold text-white mb-2">
                          {event.title}
                        </h3>
                        {event.description && (
                          <p className="text-slate-400 text-sm mb-3">
                            {event.description}
                          </p>
                        )}
                        {viewMode === "review" ? (
                          <div className="flex items-center gap-4 text-sm text-slate-500">
                            <span>
                              Closes: {event.ends_at ? format(new Date(event.ends_at), "MMM d, yyyy 'at' h:mm a") : "No end date"}
                            </span>
                            <span>•</span>
                            <span>
                              Submitted: {format(new Date(event.created_at), "MMM d, yyyy")}
                            </span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-4 text-sm text-slate-500">
                        <span>Ended: {format(new Date(event.ended_at), "MMM d, yyyy 'at' h:mm a")}</span>
                        <Button
                          onClick={() => {
                            setEditingEndedAt(event);
                            setNewEndedAt(event.ended_at ? format(new Date(event.ended_at), "yyyy-MM-dd'T'HH:mm") : "");
                          }}
                          className="text-slate-500 bg-transparent hover:text-white hover:bg-transparent"
                        >
                          [edit]
                        </Button>
                            <span>•</span>
                            <span>Traders: {event.num_traders}</span>
                            <span>•</span>
                            <span>Volume: {(event.volume / 100).toFixed(2)} G$</span>
                            <span>•</span>
                            <span>YES: {event.odds_yes}% / NO: {event.odds_no}%</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {viewMode === "review" && (
                      <div className="flex gap-3">
                        <Button
                          onClick={() => handleApprove(event.id)}
                          className="flex-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        >
                          <Check className="w-4 h-4 mr-2" />
                          Approve
                        </Button>

                        <Button
                          onClick={() => handleReject(event.id)}
                          className="flex-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 border-red-500/30"
                        >
                          <X className="w-4 h-4 mr-2" />
                          Reject
                        </Button>

                        <Button
                          onClick={() => openEdit(event)}
                          className="flex-1 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30"
                        >
                          Edit
                        </Button>
                      </div>
                    )}

                    {viewMode === "resolution" && (
                      <div className="flex gap-3">
                        <Button
                          onClick={() => {
                            if (window.confirm("Set outcome to YES? This cannot be undone.")) {
                              fetch("/api/admin/resolve", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ poll_id: event.id, outcome: true })
                              })
                                .then(async (res) => {
                                  const data = await res.json();
                                  if (data.user_profit) incrementBalance(data.user_profit);
                                  setResolveEvents(prev => prev.filter(e => e.id !== event.id));
                                })
                                .catch(err => console.error("Failed to resolve poll:", err));
                            }
                          }}
                          className="flex-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        >
                          Resolve YES
                        </Button>

                        <Button
                          onClick={() => {
                            if (window.confirm("Set outcome to NO? This cannot be undone.")) {
                              fetch("/api/admin/resolve", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ poll_id: event.id, outcome: false })
                              })
                                .then(async (res) => {
                                  const data = await res.json();
                                  if (data.user_profit) incrementBalance(data.user_profit);
                                  setResolveEvents(prev => prev.filter(e => e.id !== event.id));
                                })
                                .catch(err => console.error("Failed to resolve poll:", err));
                            }
                          }}
                          className="flex-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30"
                        >
                          Resolve NO
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      {editingEvent && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm flex justify-center items-center z-50"
          onClick={() => setEditingEvent(null)}
        >
          <div
            className="bg-slate-900 p-6 rounded-lg w-full max-w-lg border border-slate-700"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-xl font-semibold text-white mb-4">Edit Market</h2>

            <div className="space-y-4">
              <div>
                <label className="text-slate-400 text-sm">Title</label>
                <input
                  className="w-full mt-1 p-2 rounded bg-slate-800 text-white"
                  value={editValues.title}
                  onChange={(e) => setEditValues({ ...editValues, title: e.target.value })}
                />
              </div>

              <div>
                <label className="text-slate-400 text-sm">Description</label>
                <textarea
                  className="w-full mt-1 p-2 rounded bg-slate-800 text-white"
                  value={editValues.description}
                  onChange={(e) => setEditValues({ ...editValues, description: e.target.value })}
                />
              </div>

              <div>
                <label className="text-slate-400 text-sm">Tags (comma-separated)</label>
                <input
                  className="w-full mt-1 p-2 rounded bg-slate-800 text-white"
                  value={editValues.tags}
                  onChange={(e) => setEditValues({ ...editValues, tags: e.target.value })}
                />
              </div>

              <div>
                <label className="text-slate-400 text-sm">Ends At</label>
                <input
                  type="datetime-local"
                  className="w-full mt-1 p-2 rounded bg-slate-800 text-white"
                  value={
                    editValues.ends_at
                      ? format(new Date(editValues.ends_at), "yyyy-MM-dd'T'HH:mm")
                      : ""
                  }
                  onChange={(e) => setEditValues({ ...editValues, ends_at: e.target.value })}
                />
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  onClick={() => setEditingEvent(null)}
                  className="flex-1 bg-slate-700 hover:bg-slate-600"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleUpdate}
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                >
                  Update Market
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    {editingEndedAt && (
      <div
        className="fixed inset-0 bg-black/70 backdrop-blur-sm flex justify-center items-center z-50"
        onClick={() => {
          setEditingEndedAt(null);
          setNewEndedAt("");
        }}
      >
        <div
          className="bg-slate-900 p-6 rounded-lg w-full max-w-sm border border-slate-700"
          onClick={(e) => e.stopPropagation()}
        >
          <h2 className="text-xl font-semibold text-white mb-4">Edit Ended Date</h2>

          <input
            type="datetime-local"
            className="w-full mt-1 p-2 rounded bg-slate-800 text-white"
            value={newEndedAt}
            onChange={(e) => setNewEndedAt(e.target.value)}
          />

          <div className="flex gap-3 mt-6">
            <Button
              onClick={() => {
                setEditingEndedAt(null);
                setNewEndedAt("");
              }}
              className="flex-1 bg-slate-700 hover:bg-slate-600"
            >
              Cancel
            </Button>

            <Button
              onClick={handleUpdateEndedAt}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              Confirm
            </Button>
          </div>
        </div>
      </div>
    )}
    </div>
  );
}