"use client";

import { LockKeyhole, MapPin, ShieldCheck } from "lucide-react";
import Navbar from "../components/Navbar";
import { catalog, money } from "../lib/catalog";

export default function WishlistPage() {
  return <main className="min-h-screen bg-black px-5 pb-20 pt-36 text-white md:px-10"><Navbar /><div className="mx-auto max-w-7xl"><header className="mb-10 flex items-end justify-between border-b border-emerald-400/20 pb-6"><div><p className="font-mono text-xs tracking-[.3em] text-emerald-300">03 / Asset Vault</p><h1 className="mt-3 text-5xl font-semibold">Containment<span className="text-emerald-300">.</span></h1></div><LockKeyhole className="h-10 w-10 text-emerald-300" /></header><div className="space-y-4">{catalog.slice(0, 3).map((product, index) => <article key={product.id} className="grid grid-cols-[auto_1fr_auto] items-center gap-5 border border-emerald-400/20 bg-emerald-950/10 p-4 md:grid-cols-[180px_1fr_auto]"><img src={product.image} alt={product.name} className="h-24 w-24 object-cover grayscale md:h-28 md:w-40" /><div><div className="flex items-center gap-2 font-mono text-[10px] text-emerald-300"><ShieldCheck className="h-3 w-3" /> ENCRYPTED &amp; SAVED</div><h2 className="mt-2 text-xl font-semibold">{product.name}</h2><p className="mt-1 font-mono text-xs text-slate-500">VAULT_SLOT_0{index + 1} // {money(product.price)}</p></div><div className="hidden text-right font-mono text-xs text-slate-500 md:block"><MapPin className="ml-auto mb-2 h-4 w-4 text-emerald-300" />TRACKING_LOCKED<br />SIGNAL_STABLE</div></article>)}</div></div></main>;
}
