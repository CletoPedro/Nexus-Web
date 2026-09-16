"use client";

import { LogOut } from "lucide-react";

import { useAuth } from "@/components/layout/auth-guard";
import { Button } from "@/components/ui/button";

export function LogoutButton() {
  const { logout } = useAuth();

  return (
    <Button variant="ghost" size="icon" aria-label="Log out" onClick={() => logout()}>
      <LogOut />
    </Button>
  );
}
