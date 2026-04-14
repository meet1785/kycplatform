"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import { authApi } from "@/lib/api";

const otpSchema = z.object({
  code: z.string().length(6, "OTP must be 6 digits"),
});

type OTPForm = z.infer<typeof otpSchema>;

export default function VerifyOTPPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<OTPForm>({
    resolver: zodResolver(otpSchema),
  });

  const handleSendOTP = async () => {
    setIsSending(true);
    try {
      await authApi.requestOTP({ otp_type: "phone" });
      toast.success("OTP sent to your phone number.");
    } catch {
      toast.error("Failed to send OTP.");
    } finally {
      setIsSending(false);
    }
  };

  const onSubmit = async (data: OTPForm) => {
    setIsLoading(true);
    try {
      await authApi.verifyOTP({ code: data.code, otp_type: "phone" });
      toast.success("Phone number verified successfully!");
      router.push("/dashboard");
    } catch {
      toast.error("Invalid OTP. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Verify Phone</h2>
          <p className="mt-2 text-gray-600">Enter the 6-digit code sent to your phone.</p>
        </div>

        <div className="card space-y-6">
          <div className="text-center">
            <button
              onClick={handleSendOTP}
              disabled={isSending}
              className="btn-secondary text-sm"
            >
              {isSending ? "Sending..." : "Send OTP"}
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">OTP Code</label>
              <input
                {...register("code")}
                className="input-field text-center text-2xl tracking-widest"
                placeholder="000000"
                maxLength={6}
              />
              {errors.code && <p className="mt-1 text-sm text-red-600">{errors.code.message}</p>}
            </div>

            <button type="submit" disabled={isLoading} className="btn-primary w-full py-3">
              {isLoading ? "Verifying..." : "Verify"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
