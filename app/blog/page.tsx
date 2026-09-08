import { ArrowUpRight, Radio, Signal } from "lucide-react";
import Navbar from "../components/Navbar";

const transmissions = [
  ["FIELD NOTE 001", "Why precision objects outlast trends", "12.06.26"],
  ["SIGNAL REPORT 014", "Inside the new era of command hardware", "08.06.26"],
  ["OS LOG 029", "Designing a calmer digital terminal", "02.06.26"],
];

export default function BlogPage() {
  return <main className="min-h-screen bg-black px-5 pb-20 pt-36 text-white md:px-10"><Navbar /><div className="mx-auto max-w-6xl"><header className="flex flex-col justify-between gap-8 border-b border-white/10 pb-10 md:flex-row md:items-end"><div><p className="font-mono text-xs tracking-[.3em] text-purple-300">06 / Transmission Log</p><h1 className="mt-4 text-5xl font-semibold tracking-tight md:text-7xl">Signal journal<span className="text-purple-300">.</span></h1></div><Signal className="h-12 w-12 text-purple-300" /></header><div className="mt-10 grid gap-4">{transmissions.map(([tag, title, date], index) => <article key={tag} className="group grid grid-cols-[80px_1fr_auto] items-center gap-5 border border-white/10 bg-white/[.03] p-5 transition hover:border-purple-300/40 hover:bg-purple-950/10 md:grid-cols-[140px_1fr_auto]"><span className="font-mono text-[10px] text-purple-300">{tag}</span><h2 className="text-xl font-medium transition group-hover:text-purple-200 md:text-3xl">{title}</h2><div className="flex items-center gap-4 font-mono text-xs text-slate-500"><span>{date}</span><ArrowUpRight className="h-4 w-4 text-purple-300" /></div></article>)}</div><div className="mt-12 flex items-center gap-3 font-mono text-xs text-slate-500"><Radio className="h-4 w-4 text-emerald-300" /> CHANNEL OPEN // NEXT TRANSMISSION PENDING</div></div></main>;
}
