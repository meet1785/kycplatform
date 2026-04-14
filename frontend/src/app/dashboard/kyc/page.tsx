"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { kycApi } from "@/lib/api";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import KYCStatusBadge from "@/components/kyc/KYCStatusBadge";
import type { KYCApplication } from "@/types";

export default function KYCPage() {
  const queryClient = useQueryClient();

  const { data: kycApp, isLoading } = useQuery({
    queryKey: ["kyc-application"],
    queryFn: kycApi.getApplication,
  });

  const { register, handleSubmit, formState: { isDirty } } = useForm<Partial<KYCApplication>>({
    values: kycApp,
  });

  const updateMutation = useMutation({
    mutationFn: kycApi.updateApplication,
    onSuccess: () => {
      toast.success("Application updated.");
      queryClient.invalidateQueries({ queryKey: ["kyc-application"] });
    },
    onError: () => toast.error("Failed to update application."),
  });

  const submitMutation = useMutation({
    mutationFn: kycApi.submitApplication,
    onSuccess: () => {
      toast.success("Application submitted for review!");
      queryClient.invalidateQueries({ queryKey: ["kyc-application"] });
    },
    onError: (error: unknown) => {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Submission failed.");
    },
  });

  if (isLoading) {
    return <div className="card animate-pulse h-48" />;
  }

  const canSubmit = kycApp?.status === "pending" || kycApp?.status === "resubmit_required";
  const canEdit = canSubmit;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">KYC Application</h1>
        {kycApp && <KYCStatusBadge status={kycApp.status} size="lg" />}
      </div>

      {kycApp?.rejection_reason && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm font-medium text-red-800">Rejection Reason:</p>
          <p className="text-sm text-red-700 mt-1">{kycApp.rejection_reason}</p>
        </div>
      )}

      <form className="card space-y-6" onSubmit={handleSubmit((data) => updateMutation.mutate(data))}>
        <h2 className="text-lg font-semibold text-gray-900">Personal Information</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
            <input
              {...register("date_of_birth")}
              type="date"
              disabled={!canEdit}
              className="input-field disabled:bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nationality</label>
            <input
              {...register("nationality")}
              disabled={!canEdit}
              className="input-field disabled:bg-gray-100"
              placeholder="e.g. US"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 1</label>
          <input
            {...register("address_line1")}
            disabled={!canEdit}
            className="input-field disabled:bg-gray-100"
            placeholder="123 Main St"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 2</label>
          <input
            {...register("address_line2")}
            disabled={!canEdit}
            className="input-field disabled:bg-gray-100"
            placeholder="Apt 4B"
          />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
            <input {...register("city")} disabled={!canEdit} className="input-field disabled:bg-gray-100" placeholder="New York" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
            <input {...register("state")} disabled={!canEdit} className="input-field disabled:bg-gray-100" placeholder="NY" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
            <input {...register("postal_code")} disabled={!canEdit} className="input-field disabled:bg-gray-100" placeholder="10001" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
          <input {...register("country")} disabled={!canEdit} className="input-field disabled:bg-gray-100" placeholder="United States" />
        </div>

        {canEdit && (
          <button
            type="submit"
            disabled={!isDirty || updateMutation.isPending}
            className="btn-primary"
          >
            {updateMutation.isPending ? "Saving..." : "Save Changes"}
          </button>
        )}
      </form>

      {canSubmit && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Submit for Review</h2>
          <p className="text-sm text-gray-600 mb-4">
            Once submitted, your documents will be verified. Make sure you&apos;ve uploaded all required documents.
          </p>
          <button
            onClick={() => submitMutation.mutate()}
            disabled={submitMutation.isPending}
            className="btn-primary"
          >
            {submitMutation.isPending ? "Submitting..." : "Submit KYC Application"}
          </button>
        </div>
      )}
    </div>
  );
}
