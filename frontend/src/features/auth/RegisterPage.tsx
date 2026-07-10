import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Card } from "../../components/ui/Card";
import { authStorage } from "../../lib/auth";
import { getApiErrorMessage } from "../../lib/apiClient";
import { register } from "./auth.api";

export function RegisterPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const mutation = useMutation({ mutationFn: register, onSuccess: (data) => { authStorage.setToken(data.access_token); authStorage.setUser(data.user); navigate("/member/dashboard"); }, onError: (err) => setError(getApiErrorMessage(err)) });
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); setError(""); const formData = new FormData(event.currentTarget); mutation.mutate({ full_name: String(formData.get("full_name")), email: String(formData.get("email")), password: String(formData.get("password")) }); }
  return <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-12"><div className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(circle_at_15%_10%,rgba(99,102,241,.2),transparent_30rem),radial-gradient(circle_at_85%_20%,rgba(6,182,212,.18),transparent_28rem)]" /><Card className="w-full max-w-md shadow-panel"><Link to="/" className="mb-5 inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 transition hover:text-violet-700"><ArrowLeft className="h-4 w-4" />Back to home</Link><div className="mb-6"><p className="text-sm font-semibold text-brand-600">Create workspace access</p><h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Create account</h1><p className="mt-2 text-sm text-slate-500">Start submitting structured weekly updates.</p></div>{error && <div className="mb-5 rounded-2xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700 ring-1 ring-red-100">{error}</div>}<form onSubmit={handleSubmit} className="space-y-4"><Input label="Full name" name="full_name" required /><Input label="Email" name="email" type="email" required /><Input label="Password" name="password" type="password" minLength={8} required /><Button className="w-full" isLoading={mutation.isPending}>Create account</Button></form><p className="mt-6 text-center text-sm text-slate-500">Already have an account? <Link className="font-semibold text-brand-600 hover:text-brand-700" to="/login">Sign in</Link></p></Card></div>;
}
