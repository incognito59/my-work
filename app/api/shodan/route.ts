import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

interface ShodanMatch {
  ip_str?: string;
  port?: number;
  transport?: string;
  org?: string;
  timestamp?: string;
  location?: { country_name?: string; city?: string };
}

interface IntelItem {
  ip: string;
  port: number | null;
  transport: string;
  country: string;
  city: string;
  org: string;
  timestamp: string;
}

const responseCache = new Map<string, { expiresAt: number; items: IntelItem[] }>();
const rateLimits = new Map<string, number>();
const CACHE_KEY = "global-shodan-feed";
const RATE_LIMIT_MS = 15_000;
const CACHE_TTL_MS = 30_000;

function maskIp(ip?: string) {
  if (!ip) return "masked.host";
  if (ip.includes(".")) {
    const parts = ip.split(".");
    return `${parts[0]}.${parts[1]}.x.x`;
  }
  return `${ip.split(":").slice(0, 2).join(":")}:...`;
}

function sanitize(match: ShodanMatch): IntelItem {
  return {
    ip: maskIp(match.ip_str),
    port: typeof match.port === "number" ? match.port : null,
    transport: String(match.transport || "tcp").slice(0, 8),
    country: String(match.location?.country_name || "Unknown").slice(0, 64),
    city: String(match.location?.city || "Unknown").slice(0, 64),
    org: String(match.org || "Unknown").slice(0, 80),
    timestamp: String(match.timestamp || "").slice(0, 32),
  };
}

export async function GET(request: Request) {
  const apiKey = process.env.SHODAN_API_KEY;
  if (!apiKey) {
    return NextResponse.json({ success: false, error: "Shodan is not configured." }, { status: 503 });
  }

  const clientId = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "anonymous";
  const now = Date.now();
  const lastRequest = rateLimits.get(clientId) || 0;
  if (now - lastRequest < RATE_LIMIT_MS) {
    return NextResponse.json({ success: false, error: "Rate limit reached. Try again shortly." }, { status: 429 });
  }
  rateLimits.set(clientId, now);

  const cached = responseCache.get(CACHE_KEY);
  if (cached && cached.expiresAt > now) {
    return NextResponse.json({ success: true, source: "cache", items: cached.items });
  }

  const url = new URL("https://api.shodan.io/shodan/host/search");
  url.searchParams.set("key", apiKey);
  url.searchParams.set("query", process.env.SHODAN_QUERY || "ssl.cert.expired:true");
  url.searchParams.set("page", "1");

  try {
    const response = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(8_000) });
    if (!response.ok) throw new Error(`Shodan returned ${response.status}`);

    const payload = (await response.json()) as { matches?: ShodanMatch[] };
    const limit = Math.min(Math.max(Number(process.env.SHODAN_RESULTS_LIMIT || 10), 1), 10);
    const items = (payload.matches || []).filter(Boolean).slice(0, limit).map(sanitize);
    responseCache.set(CACHE_KEY, { expiresAt: now + CACHE_TTL_MS, items });

    return NextResponse.json({ success: true, source: "live", items });
  } catch {
    return NextResponse.json({ success: false, error: "Network intelligence is temporarily unavailable." }, { status: 502 });
  }
}
