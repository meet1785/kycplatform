"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import { notificationsApi } from "@/lib/api";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "🏠" },
  { href: "/dashboard/kyc", label: "KYC", icon: "📋" },
  { href: "/dashboard/documents", label: "Documents", icon: "📎" },
  { href: "/dashboard/profile", label: "Profile", icon: "👤" },
];

export default function DashboardNav() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const { data: notifications } = useQuery({
    queryKey: ["notifications"],
    queryFn: notificationsApi.getNotifications,
    refetchInterval: 30000,
  });

  const unreadCount = notifications?.results?.filter((n) => !n.is_read).length ?? 0;

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="flex items-center gap-2 font-bold text-primary-600 text-lg">
              🛡️ KYC Platform
            </Link>

            {/* Desktop nav */}
            <div className="hidden sm:flex items-center gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    pathname === item.href
                      ? "bg-primary-50 text-primary-700"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  <span>{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {unreadCount > 0 && (
              <span className="bg-red-500 text-white text-xs rounded-full px-2 py-0.5">
                {unreadCount}
              </span>
            )}
            <span className="text-sm text-gray-600 hidden sm:block">
              {user?.email}
            </span>
            <button
              onClick={logout}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
