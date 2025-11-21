import React, { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PlusCircle, CheckCircle } from "lucide-react";
import { createPageUrl } from "@/utils";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function CreateEvent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showSuccess, setShowSuccess] = useState(false);

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "Academics",
    closing_date: "",
    yes_percentage: 50,
    no_percentage: 50,
    total_pool: 0,
    status: "pending"
  });

  const createEventMutation = useMutation({
    mutationFn: (data) => base44.entities.Event.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['events']);
      setShowSuccess(true);
      setTimeout(() => {
        navigate(createPageUrl("Dashboard"));
      }, 2000);
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createEventMutation.mutate(formData);
  };

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
                  Description
                </Label>
                <Textarea
                  id="description"
                  placeholder="Add context, resolution criteria, and any relevant details..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 h-32"
                />
              </div>

              {/* Category & Date */}
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="category" className="text-slate-300">
                    Category <span className="text-red-400">*</span>
                  </Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value) => setFormData({ ...formData, category: value })}
                  >
                    <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800">
                      <SelectItem value="Academics">Academics</SelectItem>
                      <SelectItem value="Sports">Sports</SelectItem>
                      <SelectItem value="Campus Life">Campus Life</SelectItem>
                      <SelectItem value="Politics">Politics</SelectItem>
                      <SelectItem value="Weather">Weather</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="closing_date" className="text-slate-300">
                    Closing Date <span className="text-red-400">*</span>
                  </Label>
                  <Input
                    id="closing_date"
                    type="datetime-local"
                    value={formData.closing_date}
                    onChange={(e) => setFormData({ ...formData, closing_date: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                    required
                  />
                </div>
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

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold h-12 text-lg"
                disabled={createEventMutation.isPending}
              >
                {createEventMutation.isPending ? (
                  "Creating Market..."
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