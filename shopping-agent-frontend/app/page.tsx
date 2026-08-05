"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function Home() {
  const router = useRouter();
  const { token, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) return;
    router.replace(token ? "/chat" : "/login");
  }, [isLoading, token, router]);

  return null;
}
