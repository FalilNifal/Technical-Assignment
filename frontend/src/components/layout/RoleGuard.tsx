import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { authStorage } from "../../lib/auth";
import type { Role } from "../../types";

interface RoleGuardProps { allowed: Role[]; children: ReactNode; }
export function RoleGuard({ allowed, children }: RoleGuardProps) {
  const user = authStorage.getUser();
  if (!user) return <Navigate to="/login" replace />;
  if (!allowed.includes(user.role)) return <Navigate to={user.role === "TEAM_MEMBER" ? "/member/dashboard" : "/manager/dashboard"} replace />;
  return <>{children}</>;
}
