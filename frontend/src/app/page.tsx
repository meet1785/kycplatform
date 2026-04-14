import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
      <div className="max-w-2xl mx-auto text-center px-4">
        <div className="mb-8">
          <div className="w-20 h-20 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            KYC Platform
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Real-Time Know Your Customer & Communication Platform with instant
            notifications and secure document verification.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          <div className="card text-left">
            <div className="text-2xl mb-2">🔐</div>
            <h3 className="font-semibold text-gray-900 mb-1">Secure Auth</h3>
            <p className="text-sm text-gray-600">JWT + OTP via Twilio</p>
          </div>
          <div className="card text-left">
            <div className="text-2xl mb-2">📋</div>
            <h3 className="font-semibold text-gray-900 mb-1">KYC Workflow</h3>
            <p className="text-sm text-gray-600">Automated verification</p>
          </div>
          <div className="card text-left">
            <div className="text-2xl mb-2">⚡</div>
            <h3 className="font-semibold text-gray-900 mb-1">Real-Time</h3>
            <p className="text-sm text-gray-600">WebSocket updates</p>
          </div>
          <div className="card text-left">
            <div className="text-2xl mb-2">📣</div>
            <h3 className="font-semibold text-gray-900 mb-1">Notifications</h3>
            <p className="text-sm text-gray-600">SMS, WhatsApp & Email</p>
          </div>
        </div>

        <div className="flex gap-4 justify-center">
          <Link href="/auth/login" className="btn-primary text-lg px-8 py-3">
            Get Started
          </Link>
          <Link
            href="/auth/register"
            className="btn-secondary text-lg px-8 py-3"
          >
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
}
