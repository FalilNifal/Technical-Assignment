export function LoadingSkeleton() {
  return <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{Array.from({ length: 8 }).map((_, index)=><div key={index} className="h-36 animate-pulse rounded-3xl border border-white/70 bg-white/60 p-5 shadow-sm ring-1 ring-slate-900/5"><div className="h-4 w-2/3 rounded-full bg-slate-200" /><div className="mt-6 h-8 w-1/2 rounded-full bg-slate-200" /><div className="mt-5 h-3 w-full rounded-full bg-slate-100" /><div className="mt-2 h-3 w-4/5 rounded-full bg-slate-100" /></div>)}</div>;
}
