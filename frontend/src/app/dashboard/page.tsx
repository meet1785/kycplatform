"use client";

import { useQuery } from "@tanstack/react-query";
import { kycApi } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useEffect } from "react";
import toast from "react-hot-toast";
import Link from "next/link";
import KYCStatusBadge from "@/components/kyc/KYCStatusBadge";

export default function DashboardPage() {
  const { user } = useAuth();
  const { lastMessage, isConnected } = useWebSocket();

  const { data: kycApp, refetch } = useQuery({
    queryKey: ["kyc-application"],
    queryFn: kycApi.getApplication,
  });

  // Handle WebSocket KYC updates
  useEffect(() => {
    if (lastMessage?.type === "kyc_update") {
      const data = lastMessage.data as { status?: string };
      toast.success(`KYC Status Updated: ${data?.status}`);
      refetch();
    }
  }, [lastMessage, refetch]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.first_name || user?.email}!
        </h1>
        <p className="text-gray-600 mt-1">
          {isConnected ? (
            <span className="inline-flex items-center gap-1 text-green-600 text-sm">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              Real-time updates active
            </span>
          ) : (
            <span className="text-gray-400 text-sm">Connecting...</span>
          )}
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="card">
          <p className="text-sm font-medium text-gray-500">KYC Status</p>
          <div className="mt-2">
            {kycApp ? (
              <KYCStatusBadge status={kycApp.status} />
            ) : (
              <span className="text-gray-400">Loading...</span>
            )}
          </div>
        </div>

        <div className="card">
          <p className="text-sm font-medium text-gray-500">Documents</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">
            {kycApp?.documents?.length ?? 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">uploaded</p>
        </div>

        <div className="card">
          <p className="text-sm font-medium text-gray-500">Phone Verified</p>
          <p className="text-2xl font-bold mt-2">
            {user?.is_phone_verified ? (
              <span className="text-green-600">✓ Yes</span>
            ) : (
              <span className="text-red-500">✗ No</span>
            )}
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link href="/dashboard/kyc" className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600">
              📋
            </div>
            <div>
              <p className="font-medium text-gray-900">KYC Application</p>
              <p className="text-sm text-gray-500">View & update your KYC</p>
            </div>
          </Link>

          <Link href="/dashboard/documents" className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
              📎
            </div>
            <div>
              <p className="font-medium text-gray-900">Documents</p>
              <p className="text-sm text-gray-500">Upload verification docs</p>
            </div>
          </Link>

          <Link href="/dashboard/profile" className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600">
              👤
            </div>
            <div>
              <p className="font-medium text-gray-900">Profile</p>
              <p className="text-sm text-gray-500">Manage your account</p>
            </div>
          </Link>

          {!user?.is_phone_verified && (
            <Link href="/auth/verify-otp" className="flex items-center gap-3 p-4 rounded-lg border border-amber-200 bg-amber-50 hover:bg-amber-100 transition-colors">
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center text-amber-600">
                📱
              </div>
              <div>
                <p className="font-medium text-gray-900">Verify Phone</p>
                <p className="text-sm text-amber-600">Required for KYC</p>
              </div>
            </Link>
          )}
        </div>
      </div>

      {/* Recent KYC Logs */}
      {kycApp?.logs && kycApp.logs.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {kycApp.logs.slice(0, 5).map((log) => (
              <div key={log.id} className="flex items-start gap-3 text-sm">
                <span className="text-gray-400 text-xs mt-0.5 whitespace-nowrap">
                  {new Date(log.created_at).toLocaleDateString()}
                </span>
                <span className="text-gray-700">
                  {log.action.replace(/_/g, " ")}
                  {log.new_status && ` → ${log.new_status}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
