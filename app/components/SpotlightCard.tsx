"use client";

import { motion } from "framer-motion";

export default function SpotlightCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <motion.article className={`group relative overflow-hidden rounded-2xl border border-white/10 bg-white/[.035] p-6 backdrop-blur-xl shadow-[0_0_20px_rgba(6,182,212,0.15)] ${className}`} style={{ backgroundImage: "radial-gradient(420px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(34,211,238,.13), transparent 48%)" }} whileHover={{ scale: 1.018, y: -4 }} transition={{ type: "spring", stiffness: 260, damping: 22 }} onMouseMove={(event) => { const rect = event.currentTarget.getBoundingClientRect(); event.currentTarget.style.setProperty("--mouse-x", `${event.clientX - rect.left}px`); event.currentTarget.style.setProperty("--mouse-y", `${event.clientY - rect.top}px`); }}>{children}</motion.article>;
}
