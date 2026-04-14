"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { kycApi } from "@/lib/api";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";

const DOCUMENT_TYPES = [
  { value: "passport", label: "Passport" },
  { value: "national_id", label: "National ID" },
  { value: "drivers_license", label: "Driver's License" },
  { value: "utility_bill", label: "Utility Bill" },
  { value: "bank_statement", label: "Bank Statement" },
  { value: "selfie", label: "Selfie" },
  { value: "other", label: "Other" },
];

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const [selectedType, setSelectedType] = useState("passport");

  const { data: documents, isLoading } = useQuery({
    queryKey: ["kyc-documents"],
    queryFn: kycApi.getDocuments,
  });

  const uploadMutation = useMutation({
    mutationFn: kycApi.uploadDocument,
    onSuccess: () => {
      toast.success("Document uploaded successfully!");
      queryClient.invalidateQueries({ queryKey: ["kyc-documents"] });
      queryClient.invalidateQueries({ queryKey: ["kyc-application"] });
    },
    onError: (error: unknown) => {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Upload failed.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: kycApi.deleteDocument,
    onSuccess: () => {
      toast.success("Document deleted.");
      queryClient.invalidateQueries({ queryKey: ["kyc-documents"] });
    },
    onError: (error: unknown) => {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Delete failed.");
    },
  });

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      acceptedFiles.forEach((file) => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("document_type", selectedType);
        uploadMutation.mutate(formData);
      });
    },
    [selectedType, uploadMutation]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpg", ".jpeg", ".png"],
      "application/pdf": [".pdf"],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Documents</h1>

      {/* Upload Section */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Upload Document</h2>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="input-field"
          >
            {DOCUMENT_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-primary-400 bg-primary-50"
              : "border-gray-300 hover:border-primary-300 hover:bg-gray-50"
          }`}
        >
          <input {...getInputProps()} />
          <div className="text-4xl mb-3">📎</div>
          {isDragActive ? (
            <p className="text-primary-600 font-medium">Drop files here...</p>
          ) : (
            <>
              <p className="text-gray-700 font-medium">
                Drag & drop files here, or click to select
              </p>
              <p className="text-sm text-gray-500 mt-1">
                PDF, JPG, PNG up to 10MB
              </p>
            </>
          )}
          {uploadMutation.isPending && (
            <p className="text-primary-600 mt-2">Uploading...</p>
          )}
        </div>
      </div>

      {/* Documents List */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Uploaded Documents ({documents?.length ?? 0})
        </h2>

        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : documents?.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No documents uploaded yet.</p>
        ) : (
          <div className="space-y-3">
            {documents?.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                    📄
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{doc.file_name}</p>
                    <p className="text-xs text-gray-500">
                      {DOCUMENT_TYPES.find((t) => t.value === doc.document_type)?.label} •{" "}
                      {formatFileSize(doc.file_size)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {doc.is_verified && (
                    <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                      ✓ Verified
                    </span>
                  )}
                  <button
                    onClick={() => deleteMutation.mutate(doc.id)}
                    disabled={deleteMutation.isPending}
                    className="text-red-500 hover:text-red-700 text-sm px-2 py-1"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
