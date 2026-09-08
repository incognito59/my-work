"use client";

import { motion } from "framer-motion";
import { Activity, ArrowUpRight, Cpu, Radar, RefreshCw, Search, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import Navbar from "./components/Navbar";

type IntelItem = { ip: string; port: number | null; transport: string; country: string; city: string; org: string; timestamp: string };
type Product = { name: string; category: string; price: string; image: string; detail: string };

const products: Product[] = [
  { name: "Rolex Submariner", category: "Precision asset", price: "$14,250", detail: "Ceramic bezel // 300m depth", image: "https://images.unsplash.com/photo-1547996160-81dfa63595aa?auto=format&fit=crop&w=1200&q=85" },
  { name: "MacBook Pro M4", category: "Command hardware", price: "$2,499", detail: "M4 Pro // 36GB unified memory", image: "https://images.unsplash.com/photo-1517336714739-489689fd1ca8?auto=format&fit=crop&w=1200&q=85" },
];

function SpotlightCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.article
      className={`group relative overflow-hidden rounded-2xl border border-white/10 bg-white/[.035] p-6 backdrop-blur-xl ${className}`}
      style={{ backgroundImage: "radial-gradient(420px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(34,211,238,.13), transparent 48%)" }}
      whileHover={{ scale: 1.018, y: -4 }}
      transition={{ type: "spring", stiffness: 260, damping: 22 }}
      onMouseMove={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        event.currentTarget.style.setProperty("--mouse-x", `${event.clientX - rect.left}px`);
        event.currentTarget.style.setProperty("--mouse-y", `${event.clientY - rect.top}px`);
      }}
    >{children}</motion.article>
  );
}

export default function HomePage() {
  const [intel, setIntel] = useState<IntelItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [command, setCommand] = useState("");
  const [updated, setUpdated] = useState("Awaiting telemetry");

  async function loadIntel() {
    setLoading(true);
    try {
      const response = await fetch("/api/shodan", { cache: "no-store" });
      const payload = (await response.json()) as { success?: boolean; items?: IntelItem[]; error?: string };
      if (!response.ok || !payload.success) throw new Error(payload.error || "Feed unavailable");
      setIntel(payload.items || []);
      setUpdated(`Updated ${new Date().toLocaleTimeString()}`);
    } catch (error) {
      setUpdated(error instanceof Error ? error.message : "Feed unavailable");
    } finally { setLoading(false); }
  }

  useEffect(() => { loadIntel(); }, []);

  const terminalItems = intel.length ? intel : [{ ip: "masked.host", port: 443, transport: "tcp", country: "Awaiting", city: "signal", org: "SHODAN_NODE", timestamp: "--:--" }];

  return (
    <main className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="mx-auto max-w-7xl px-5 pb-16 pt-36 md:px-8">
        <header className="mb-10 flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div><p className="mb-3 flex items-center gap-2 font-mono text-xs uppercase tracking-[.25em] text-cyan-300"><span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_14px_#34d399]" /> RedCart / Command Center</p><h1 className="text-4xl font-bold tracking-tight md:text-7xl">Luxury commerce.<br /><span className="text-cyan-300 [text-shadow:0_0_22px_rgba(34,211,238,.35)]">Live intelligence.</span></h1></div>
          <div className="flex items-center gap-3 rounded-xl border border-emerald-400/20 bg-emerald-400/5 px-4 py-3 font-mono text-xs text-emerald-300"><Activity className="h-4 w-4" /> SYSTEM OPERATIONAL</div>
        </header>

        <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <SpotlightCard className="md:col-span-2">
            <div className="mb-8 flex items-center justify-between"><div className="flex items-center gap-3"><Cpu className="text-cyan-300" /><h2 className="font-mono text-sm uppercase tracking-widest">System Search Terminal</h2></div><span className="font-mono text-xs text-emerald-300">ONLINE</span></div>
            <div className="crt-scanlines rounded-xl border border-cyan-400/20 bg-black/80 p-5 font-mono text-sm text-cyan-300"><p>$ initialize redcart_core</p><p className="mt-2 text-emerald-300">✓ premium vault mounted</p><p className="text-emerald-300">✓ network intelligence ready</p><p className="mt-2">$ {command || "awaiting operator command"}<span className="ml-1 animate-pulse">▌</span></p><div className="mt-5 flex gap-2"><input value={command} onChange={(event) => setCommand(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") setCommand(""); }} placeholder="type a command..." className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-slate-600" /><button onClick={() => setCommand("")} className="rounded-md border border-cyan-400/30 px-3 py-2 text-cyan-300 hover:bg-cyan-400/10"><Search className="h-4 w-4" /></button></div></div>
          </SpotlightCard>

          {products.map((product) => <SpotlightCard key={product.name} className="p-0"><div className="relative aspect-[4/5] overflow-hidden"><img src={product.image} alt={product.name} className="h-full w-full object-cover transition duration-700 group-hover:scale-110" /><div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent" /><div className="absolute bottom-0 p-5"><p className="font-mono text-xs uppercase tracking-widest text-cyan-300">{product.category}</p><h2 className="mt-2 text-xl font-semibold">{product.name}</h2><p className="mt-2 text-sm text-slate-400">{product.detail}</p><p className="mt-2 text-slate-200">{product.price}</p></div><ArrowUpRight className="absolute right-5 top-5 text-white/70" /></div></SpotlightCard>)}

          <SpotlightCard className="md:col-span-2"><div className="mb-5 flex items-center justify-between"><div className="flex items-center gap-3"><Radar className="text-cyan-300" /><h2 className="font-mono text-sm uppercase tracking-widest">Live Shodan Threat Stream</h2></div><span className="flex items-center gap-2 font-mono text-xs text-red-400"><span className="h-2 w-2 animate-pulse rounded-full bg-red-500" /> LIVE</span></div><div className="max-h-72 space-y-3 overflow-auto rounded-xl border border-cyan-400/20 bg-black/80 p-4 font-mono text-xs">{loading && <p className="text-slate-500">connecting to intelligence relay...</p>}{terminalItems.map((item, index) => <motion.div key={`${item.ip}-${item.port}-${index}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="border-b border-white/5 pb-2 text-cyan-300"><span className="text-slate-600">{item.timestamp || "--:--"}</span> {item.ip}:{item.port ?? "—"}/{item.transport}<span className="ml-2 text-slate-500">{item.country} · {item.org}</span></motion.div>)}</div><div className="mt-4 flex items-center justify-between"><span className="font-mono text-xs text-slate-600">{updated}</span><button onClick={loadIntel} disabled={loading} className="flex items-center gap-2 rounded-md border border-cyan-400/30 px-3 py-2 font-mono text-xs text-cyan-300 hover:bg-cyan-400/10 disabled:opacity-50"><RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} /> Refresh</button></div></SpotlightCard>
          <SpotlightCard><div className="flex items-center gap-3"><ShieldCheck className="text-cyan-300" /><h2 className="font-mono text-sm uppercase tracking-widest">Signal posture</h2></div><div className="mx-auto my-10 grid h-36 w-36 place-items-center rounded-full border border-cyan-300/30 text-cyan-300 shadow-[0_0_0_16px_rgba(34,211,238,.04),0_0_60px_rgba(34,211,238,.16)]"><span className="font-mono text-xs tracking-[.25em]">SECURE</span></div><p className="text-sm leading-6 text-slate-400">Server-side API boundaries, masked hosts, and bounded responses keep the intelligence surface focused.</p></SpotlightCard>
        </section>
      </div>
    </main>
  );
}
