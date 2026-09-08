import { ShieldCheck } from "lucide-react";
import Link from "next/link";

const footerGroups = [
  { title: "Navigate", links: [["Home", "/"], ["Shop", "/shop"], ["Asset Vault", "/wishlist"], ["Ledger", "/cart"]] },
  { title: "Platform", links: [["Signal Journal", "/blog"], ["About OS", "/about"], ["Gateway", "/auth"]] },
  { title: "Protocol", links: [["Privacy", "/privacy"], ["Terms", "/terms"], ["Security", "/security"]] },
];

export default function Footer() {
  return <footer className="rc-os-footer"><div className="rc-os-footer__inner"><div className="rc-os-footer__grid"><div className="rc-os-footer__identity"><Link href="/" className="rc-os-footer__brand">RED<span>/CART_OS</span></Link><p>Premium objects and live intelligence for a more considered digital world.</p><div className="rc-os-footer__status"><ShieldCheck className="h-4 w-4" /> ENCRYPTED COMMERCE CHANNEL</div></div>{footerGroups.map((group) => <div key={group.title} className="rc-os-footer__column"><h2>{group.title}</h2>{group.links.map(([label, href]) => <Link key={label} href={href}>{label}</Link>)}</div>)}<div className="rc-os-footer__column"><h2>Connect</h2><div className="rc-os-footer__social"><a href="#" aria-label="Instagram">IG</a><a href="#" aria-label="LinkedIn">IN</a><a href="#" aria-label="Github">GH</a></div><p className="rc-os-footer__micro">SYSTEM STATUS: NOMINAL<br />NODE: GLOBAL_PRIORITY</p></div></div><div className="rc-os-footer__bottom"><span>© 2026 RED/CART_OS</span><span>BUILD 1.0.0 // ALL SYSTEMS RESERVED</span></div></div></footer>;
}
