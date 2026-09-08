export type Product = {
  id: string;
  name: string;
  category: string;
  price: number;
  image: string;
  specs: string[];
  status: string;
  inventory: number;
};

export const catalog: Product[] = [
  { id: "submariner", name: "Rolex Submariner", category: "Precision Asset", price: 14250000, inventory: 9, image: "https://images.unsplash.com/photo-1547996160-81dfa63595aa?auto=format&fit=crop&w=1400&q=85", specs: ["Ceramic bezel", "300m water resistance", "Automatic calibre 3230"], status: "Vault verified" },
  { id: "macbook-m4", name: "MacBook Pro M4", category: "Command Hardware", price: 2499000, inventory: 90, image: "https://images.unsplash.com/photo-1517336714739-489689fd1ca8?auto=format&fit=crop&w=1400&q=85", specs: ["M4 Pro neural engine", "36GB unified memory", "14.2-inch Liquid Retina XDR"], status: "Ready to ship" },
  { id: "leica-q3", name: "Leica Q3", category: "Optical Instrument", price: 6295000, inventory: 12, image: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=1400&q=85", specs: ["60.3MP full-frame", "Summilux 28mm lens", "8K cinematic capture"], status: "Two units located" },
  { id: "audio-x", name: "Audeze LCD-X", category: "Acoustic System", price: 1199000, inventory: 24, image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1400&q=85", specs: ["Planar magnetic drivers", "20Hz-20kHz range", "Studio reference profile"], status: "Signal clean" },
];

export const money = (value: number) => `₦${value.toLocaleString("en-NG", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
