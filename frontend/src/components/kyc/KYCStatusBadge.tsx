import type { KYCStatus } from "@/types";

interface KYCStatusBadgeProps {
  status: KYCStatus;
  size?: "sm" | "md" | "lg";
}

const statusConfig: Record<
  KYCStatus,
  { label: string; className: string; icon: string }
> = {
  pending: {
    label: "Pending",
    className: "bg-gray-100 text-gray-700",
    icon: "⏳",
  },
  processing: {
    label: "Processing",
    className: "bg-blue-100 text-blue-700",
    icon: "🔄",
  },
  approved: {
    label: "Approved",
    className: "bg-green-100 text-green-700",
    icon: "✅",
  },
  rejected: {
    label: "Rejected",
    className: "bg-red-100 text-red-700",
    icon: "❌",
  },
  resubmit_required: {
    label: "Resubmit Required",
    className: "bg-amber-100 text-amber-700",
    icon: "⚠️",
  },
};

const sizeClasses = {
  sm: "text-xs px-2 py-0.5",
  md: "text-sm px-2.5 py-1",
  lg: "text-base px-3 py-1.5",
};

export default function KYCStatusBadge({
  status,
  size = "md",
}: KYCStatusBadgeProps) {
  const config = statusConfig[status] ?? statusConfig.pending;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${config.className} ${sizeClasses[size]}`}
    >
      <span>{config.icon}</span>
      {config.label}
    </span>
  );
}
