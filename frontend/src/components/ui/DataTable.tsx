import type { ReactNode } from "react";

interface DataTableProps { children: ReactNode; minWidth?: string; }
export function DataTable({ children, minWidth = "760px" }: DataTableProps) {
  return <div className="overflow-hidden rounded-3xl border border-violet-100 bg-white/80 shadow-sm ring-1 ring-violet-100/60"><div className="overflow-x-auto"><table className="w-full text-left text-sm" style={{ minWidth }}>{children}</table></div></div>;
}
