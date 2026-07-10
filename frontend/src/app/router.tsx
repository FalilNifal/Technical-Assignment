import { createBrowserRouter, Navigate } from "react-router-dom";
import { LandingPage } from "../features/landing/LandingPage";
import { LoginPage } from "../features/auth/LoginPage";
import { RegisterPage } from "../features/auth/RegisterPage";
import { MemberDashboardPage } from "../features/reports/MemberDashboardPage";
import { CreateReportPage } from "../features/reports/CreateReportPage";
import { EditReportPage } from "../features/reports/EditReportPage";
import { ReportHistoryPage } from "../features/reports/ReportHistoryPage";
import { ManagerDashboardPage } from "../features/dashboard/ManagerDashboardPage";
import { ProjectsPage } from "../features/projects/ProjectsPage";
import { ProtectedRoute } from "../components/layout/ProtectedRoute";
import { RoleGuard } from "../components/layout/RoleGuard";

export const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  { path: "/member/dashboard", element: <ProtectedRoute><RoleGuard allowed={["TEAM_MEMBER"]}><MemberDashboardPage /></RoleGuard></ProtectedRoute> },
  { path: "/member/reports/new", element: <ProtectedRoute><RoleGuard allowed={["TEAM_MEMBER"]}><CreateReportPage /></RoleGuard></ProtectedRoute> },
  { path: "/member/reports/:reportId/edit", element: <ProtectedRoute><RoleGuard allowed={["TEAM_MEMBER"]}><EditReportPage /></RoleGuard></ProtectedRoute> },
  { path: "/member/reports/history", element: <ProtectedRoute><RoleGuard allowed={["TEAM_MEMBER"]}><ReportHistoryPage /></RoleGuard></ProtectedRoute> },
  { path: "/manager/dashboard", element: <ProtectedRoute><RoleGuard allowed={["MANAGER", "ADMIN"]}><ManagerDashboardPage /></RoleGuard></ProtectedRoute> },
  { path: "/manager/projects", element: <ProtectedRoute><RoleGuard allowed={["MANAGER", "ADMIN"]}><ProjectsPage /></RoleGuard></ProtectedRoute> },
  { path: "*", element: <Navigate to="/" replace /> },
]);
