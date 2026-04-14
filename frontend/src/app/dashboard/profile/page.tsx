"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/lib/api";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { useAuth } from "@/hooks/useAuth";
import type { User } from "@/types";

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const { user, logout } = useAuth();

  const { register, handleSubmit, formState: { isDirty } } = useForm<Partial<User>>({
    values: user,
  });

  const updateMutation = useMutation({
    mutationFn: authApi.updateProfile,
    onSuccess: () => {
      toast.success("Profile updated.");
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: () => toast.error("Failed to update profile."),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Profile</h1>

      <form
        className="card space-y-6"
        onSubmit={handleSubmit((data) => updateMutation.mutate(data))}
      >
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center text-3xl">
            {user?.first_name?.[0] || user?.email?.[0] || "U"}
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {user?.first_name} {user?.last_name}
            </h2>
            <p className="text-gray-500">{user?.email}</p>
            <div className="flex gap-2 mt-1">
              <span className={`text-xs px-2 py-0.5 rounded-full ${user?.is_phone_verified ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
                Phone {user?.is_phone_verified ? "✓ Verified" : "Not Verified"}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
            <input {...register("first_name")} className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
            <input {...register("last_name")} className="input-field" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input {...register("email")} type="email" disabled className="input-field bg-gray-100 cursor-not-allowed" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
          <input {...register("phone_number")} className="input-field" placeholder="+1234567890" />
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!isDirty || updateMutation.isPending}
            className="btn-primary"
          >
            {updateMutation.isPending ? "Saving..." : "Save Changes"}
          </button>
          <button
            type="button"
            onClick={logout}
            className="btn-secondary text-red-600 hover:text-red-700"
          >
            Sign Out
          </button>
        </div>
      </form>
    </div>
  );
}
