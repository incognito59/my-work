"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Activity, Heart, Menu, ShoppingBag, Terminal, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const links = ["Home", "Shop", "Blog", "About"];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [ping, setPing] = useState(24);

  useEffect(() => {
    const timer = window.setInterval(() => setPing(20 + Math.floor(Math.random() * 26)), 3000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-black px-6 py-4 backdrop-blur-xl">
      <div className="mx-auto grid min-w-0 grid-cols-1 items-center gap-4 md:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] md:gap-6">
        <Link href="/" className="flex w-auto min-w-0 shrink-0 items-center gap-3" aria-label="RedCart home">
          <span className="relative grid h-9 w-9 place-items-center rounded-full border border-cyan-300/80 shadow-[0_0_22px_rgba(34,211,238,.3)]">
            <span className="h-2 w-2 rounded-full bg-cyan-200 shadow-[0_0_14px_#22d3ee]" />
            <span className="absolute h-5 w-10 rotate-45 rounded-full border border-purple-400/70" />
          </span>
          <span className="font-mono text-sm font-bold tracking-[.24em] text-white">RED<span className="text-cyan-300">CART</span></span>
        </Link>

        <div className="hidden min-w-0 items-center justify-center md:flex">
          <nav className="flex w-max max-w-full items-center gap-8 overflow-x-auto rounded-full border border-white/10 bg-white/[.045] px-5 py-1" aria-label="Primary navigation">
            {links.map((link) => (
              <Link key={link} href={link === "Home" ? "/" : `/${link.toLowerCase()}`} className="group relative shrink-0 rounded-full px-1 py-2 font-mono text-xs text-slate-400 transition hover:text-white">
                <span className="absolute inset-x-3 bottom-0 h-px origin-left scale-x-0 bg-cyan-300 shadow-[0_0_12px_#22d3ee] transition-transform duration-200 group-hover:scale-x-100" />
                {link}
              </Link>
            ))}
          </nav>
        </div>

        <div className="ml-0 flex w-auto min-w-0 shrink-0 items-center justify-self-end gap-2 md:ml-4">
          <div className="hidden w-auto max-w-[230px] flex-shrink-0 items-center gap-2 rounded border border-emerald-500/30 bg-emerald-950/30 px-3 py-1 font-mono text-xs text-emerald-400 lg:flex">
            <span className="h-1.5 w-1.5 shrink-0 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]" />
            <span className="truncate">SHODAN_NODE: CONNECTED // <strong className="text-emerald-200 [text-shadow:0_0_8px_rgba(74,222,128,.85)]">{ping}ms</strong></span>
          </div>

          <Link href="/wishlist" className="hidden items-center gap-1.5 rounded-md px-2 py-2 font-mono text-[11px] text-slate-400 transition hover:bg-white/5 hover:text-white sm:flex"><Heart className="h-4 w-4 text-cyan-300/80" /> Wishlist</Link>
          <Link href="/cart" className="relative flex items-center gap-1.5 rounded-md px-2 py-2 font-mono text-[11px] text-slate-400 transition hover:bg-white/5 hover:text-white"><ShoppingBag className="h-4 w-4 text-cyan-300/80" /><span className="hidden sm:inline">Cart</span><b className="absolute -right-1 -top-1 grid h-4 min-w-4 place-items-center rounded-full bg-cyan-300 px-1 text-[9px] text-black">0</b></Link>
          <Link href="/auth" className="hidden px-2 py-2 font-mono text-[11px] text-slate-400 hover:text-white sm:block">Login</Link>
          <Link href="/auth" className="hidden rounded-md border border-cyan-300/50 bg-cyan-300/10 px-3 py-2 font-mono text-[11px] text-cyan-200 transition hover:bg-cyan-300/20 sm:block">Register</Link>
          <button type="button" onClick={() => setOpen(true)} className="grid h-9 w-9 place-items-center rounded-md border border-white/10 bg-white/5 text-slate-300 hover:text-cyan-200 md:hidden" aria-label="Open navigation"><Menu className="h-4 w-4" /></button>
        </div>
      </div>

      <div className="mx-auto hidden w-full max-w-2xl px-5 pb-3 md:block">
        <div className="flex h-8 min-w-0 items-center gap-2 rounded-md border border-white/10 bg-white/[.04] px-3">
          <Terminal className="h-3 w-3 text-cyan-300" />
          <input className="min-w-0 flex-1 bg-transparent font-mono text-[10px] text-white outline-none placeholder:text-slate-600" placeholder="Search the RedCart index..." />
          <button className="font-mono text-[9px] tracking-widest text-cyan-300 hover:text-white">EXECUTE</button>
        </div>
      </div>

      <AnimatePresence>
        {open && (
          <motion.aside initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }} transition={{ type: "spring", stiffness: 300, damping: 30 }} className="fixed right-0 top-0 h-screen w-[min(88vw,360px)] border-l border-cyan-300/20 bg-black p-6 shadow-[-20px_0_80px_rgba(0,0,0,.7)] md:hidden">
            <div className="flex items-center justify-between border-b border-white/10 pb-5 font-mono text-xs tracking-[.2em] text-cyan-300"><span>RED/CART_OS</span><button onClick={() => setOpen(false)} aria-label="Close navigation"><X className="h-4 w-4" /></button></div>
            <div className="mt-6 flex items-center gap-2 font-mono text-[9px] tracking-widest text-emerald-300"><Activity className="h-3 w-3" /> SHODAN_NODE: CONNECTED</div>
            <nav className="mt-8 flex flex-col gap-2">{[...links, "Wishlist", "Cart", "Login", "Register"].map((link, index) => <Link key={link} href={link === "Home" ? "/" : ["Login", "Register"].includes(link) ? "/auth" : `/${link.toLowerCase()}`} onClick={() => setOpen(false)} className="border-b border-white/5 py-3 font-mono text-sm text-slate-400 hover:border-cyan-300/40 hover:text-cyan-200">0{index + 1} / {link}</Link>)}</nav>
          </motion.aside>
        )}
      </AnimatePresence>
    </header>
  );
}
