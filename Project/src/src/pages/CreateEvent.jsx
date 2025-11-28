import React, { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/context/AuthContext";
import { PlusCircle, CheckCircle, Tag, CalendarClock, Loader2 } from "lucide-react";
import { createPageUrl } from "@/utils";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function CreateEvent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { userId } = useAuth();
  const [showSuccess, setShowSuccess] = useState(false);
  const [formError, setFormError] = useState("");
  const TAGS_PER_PAGE = 8;

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    closing_date: ""
  });

  const [selectedTags, setSelectedTags] = useState([]);
  const [tagPage, setTagPage] = useState(1);

  const { data: tags = [], isLoading: tagsLoading } = useQuery({
    queryKey: ["tags"],
    queryFn: async () => {
      const res = await fetch("/api/tags/all");
      if (!res.ok) throw new Error("Failed to load tags");
      const json = await res.json();
      const rawTags = json.tags || [];
      return rawTags.map((t) => ({
        id: Number(t.id),
        name: t.name
      })).filter((t) => !Number.isNaN(t.id));
    }
  });

  useEffect(() => {
    if (tags.length === 0) return;
    const maxPage = Math.max(1, Math.ceil(tags.length / TAGS_PER_PAGE));
    if (tagPage > maxPage) setTagPage(maxPage);
  }, [tags, tagPage]);

  const createEventMutation = useMutation({
    mutationFn: async (payload) => {
      const res = await fetch("/api/polls", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const json = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(json.error || "Failed to create market");
      }

      return json;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(["polls"]);
      setShowSuccess(true);
      setFormError("");
      setFormData({ title: "", description: "", closing_date: "" });
      setSelectedTags([]);
      setTimeout(() => {
        navigate(createPageUrl("Dashboard"));
      }, 2000);
    },
    onError: (error) => {
      setFormError(error.message || "Unable to create market");
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setFormError("");

    if (!userId) {
      setFormError("You need to be signed in to create a market.");
      return;
    }

    if (!formData.closing_date) {
      setFormError("Please choose a closing date and time.");
      return;
    }

    const endsAt = new Date(formData.closing_date);
    if (isNaN(endsAt.getTime())) {
      setFormError("Please provide a valid closing date and time.");
      return;
    }

    const payload = {
      title: formData.title.trim(),
      description: formData.description.trim(),
      ends_at: endsAt.toISOString(),
      public: true,
      creator: userId,
      tags: selectedTags.map(Number)
    };

    createEventMutation.mutate(payload);
  };

  const toggleTag = (tagId) => {
    const normalizedId = Number(tagId);
    if (Number.isNaN(normalizedId)) return;
    setSelectedTags((prev) =>
      prev.includes(normalizedId)
        ? prev.filter((id) => id !== normalizedId)
        : [...prev, normalizedId]
    );
  };

  const totalTagPages = Math.max(1, Math.ceil(tags.length / TAGS_PER_PAGE));
  const visibleTags = tags.slice((tagPage - 1) * TAGS_PER_PAGE, tagPage * TAGS_PER_PAGE);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-3xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-violet-500/20">
              <PlusCircle className="w-6 h-6 text-emerald-400" />
            </div>
            <h1 className="text-4xl font-bold text-white">Create Market</h1>
          </div>
          <p className="text-slate-400 text-lg">
            Propose a new prediction market for the UWaterloo community
          </p>
        </div>

        {showSuccess && (
          <Alert className="mb-6 border-emerald-500/30 bg-emerald-500/10">
            <CheckCircle className="h-4 w-4 text-emerald-400" />
            <AlertDescription className="text-emerald-400">
              Market created successfully! Redirecting to dashboard...
            </AlertDescription>
          </Alert>
        )}

        {/* Form */}
        <Card className="border-slate-800 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="text-white">Market Details</CardTitle>
            <CardDescription className="text-slate-400">
              Your market will be reviewed by admins before going live
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Title */}
              <div className="space-y-2">
                <Label htmlFor="title" className="text-slate-300">
                  Market Question <span className="text-red-400">*</span>
                </Label>
                <Input
                  id="title"
                  placeholder="e.g., Will the CSC 369 midterm average exceed 70%?"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                  required
                />
                <p className="text-xs text-slate-500">
                  Make it clear and verifiable. Yes/No questions work best.
                </p>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description" className="text-slate-300">
                  Description <span className="text-red-400">*</span>
                </Label>
                <Textarea
                  id="description"
                  placeholder="Add context, resolution criteria, and any relevant details..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 h-32"
                  required
                />
              </div>

              {/* Date */}
              <div className="space-y-3">
                <Label htmlFor="closing_date" className="text-slate-300">
                  Closing Date <span className="text-red-400">*</span>
                </Label>
                <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-inner">
                  <div className="flex flex-col md:flex-row md:items-center md:gap-4">
                    <div className="flex items-center gap-3 mb-3 md:mb-0">
                      <div className="rounded-lg bg-emerald-500/10 p-3 border border-emerald-500/20">
                        <CalendarClock className="w-5 h-5 text-emerald-400" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-300 font-semibold">When does this market close?</p>
                        <p className="text-xs text-slate-500">Pick a date and time in the future.</p>
                      </div>
                    </div>
                    <div className="flex-1">
                      <Input
                        id="closing_date"
                        type="datetime-local"
                        value={formData.closing_date}
                        onChange={(e) => setFormData({ ...formData, closing_date: e.target.value })}
                        className="bg-slate-800 border border-slate-700 text-white focus:border-emerald-500 focus:ring-emerald-500/50"
                        required
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Tags */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-slate-300">Tags</Label>
                    <p className="text-xs text-slate-500">Choose tags that help others find this market.</p>
                  </div>
                  <Badge variant="outline" className="border-emerald-600/40 bg-emerald-500/10 text-emerald-100 font-semibold">
                    {selectedTags.length} selected
                  </Badge>
                </div>
                <div className="grid sm:grid-cols-2 gap-2">
                  {tagsLoading ? (
                    <div className="flex items-center gap-2 text-slate-500">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Loading tags...
                    </div>
                  ) : tags.length === 0 ? (
                    <p className="text-slate-500 text-sm">No tags available yet.</p>
                  ) : (
                    visibleTags.map((tag) => {
                      const isActive = selectedTags.includes(tag.id);
                      return (
                        <button
                          key={tag.id}
                          type="button"
                          onClick={() => toggleTag(tag.id)}
                          aria-pressed={isActive}
                          className={`flex items-center justify-between rounded-lg border px-3 py-2 transition ${
                            isActive
                              ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-100"
                              : "border-slate-800 bg-slate-900/60 text-slate-300 hover:border-emerald-500/40 hover:text-white"
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            <Tag className="w-4 h-4" />
                            <span className="text-sm font-medium">{tag.name}</span>
                          </div>
                          {isActive && <CheckCircle className="w-4 h-4 text-emerald-400" />}
                        </button>
                      );
                    })
                  )}
                </div>
                {totalTagPages > 1 && (
                  <div className="flex items-center justify-end gap-3 text-sm text-slate-400">
                    <button
                      type="button"
                      onClick={() => setTagPage((p) => Math.max(1, p - 1))}
                      disabled={tagPage === 1}
                      className="px-3 py-1 rounded-lg border border-slate-700 bg-slate-800/60 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:border-emerald-500/40"
                    >
                      Prev
                    </button>
                    <span className="text-slate-300">
                      Page {tagPage} / {totalTagPages}
                    </span>
                    <button
                      type="button"
                      onClick={() => setTagPage((p) => Math.min(totalTagPages, p + 1))}
                      disabled={tagPage === totalTagPages}
                      className="px-3 py-1 rounded-lg border border-slate-700 bg-slate-800/60 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:border-emerald-500/40"
                    >
                      Next
                    </button>
                  </div>
                )}
                {selectedTags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedTags.map((tagId) => {
                      const tagObj = tags.find((t) => t.id === tagId);
                      if (!tagObj) return null;
                      return (
                        <Badge
                          key={tagId}
                          variant="outline"
                          className="bg-slate-800/70 border-slate-700 text-slate-100"
                        >
                          {tagObj.name}
                        </Badge>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Info Box */}
              <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
                <div className="flex gap-3">
                  <span className="text-2xl">ℹ️</span>
                  <div>
                    <h4 className="text-white font-semibold mb-1">Submission Guidelines</h4>
                    <ul className="text-sm text-slate-400 space-y-1">
                      <li>• Markets must be resolvable with a clear Yes/No answer</li>
                      <li>• Closing date should be before the event occurs</li>
                      <li>• Admins will review within 24 hours</li>
                      <li>• Markets start with 50/50 odds</li>
                    </ul>
                  </div>
                </div>
              </div>

              {formError && (
                <Alert className="border-red-500/30 bg-red-500/10">
                  <AlertDescription className="text-red-300 text-sm">
                    {formError}
                  </AlertDescription>
                </Alert>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold h-12 text-lg"
                disabled={createEventMutation.isPending}
              >
                {createEventMutation.isPending ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Creating Market...
                  </span>
                ) : (
                  <>
                    <PlusCircle className="w-5 h-5 mr-2" />
                    Create Market
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
