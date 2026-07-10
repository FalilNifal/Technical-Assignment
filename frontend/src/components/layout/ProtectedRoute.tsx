import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { authStorage } from "../../lib/auth";

interface ProtectedRouteProps { children: ReactNode; }
export function ProtectedRoute({ children }: ProtectedRouteProps) {
  return authStorage.getToken() ? <>{children}</> : <Navigate to="/login" replace />;
}
