import type { Product, ProductView } from "@/lib/types";

type ProductMeta = {
  emoji: string;
  company: string;
  model?: string;
  docs: number;
  sessions: number;
  resolutionRate: number;
  manufacturer: string;
  year: string;
  productType: string;
  featured?: boolean;
};

const metaById: Record<string, ProductMeta> = {
  "hp-laserjet-pro-m404n": {
    emoji: "🖨",
    company: "HP Inc.",
    model: "Model 2021",
    docs: 12,
    sessions: 4281,
    resolutionRate: 87,
    manufacturer: "HP Inc.",
    year: "2021 - Present",
    productType: "Monochrome Laser Printer",
  },
  "daikin-ftxm35tvma": {
    emoji: "❄️",
    company: "Daikin Industries",
    docs: 8,
    sessions: 1673,
    resolutionRate: 89,
    manufacturer: "Daikin Industries",
    year: "2020 - Present",
    productType: "Split Air Conditioner",
    featured: true,
  },
  "caterpillar-320-gc": {
    emoji: "⚙️",
    company: "Caterpillar Inc.",
    docs: 24,
    sessions: 3150,
    resolutionRate: 84,
    manufacturer: "Caterpillar Inc.",
    year: "2019 - Present",
    productType: "Hydraulic Excavator",
  },
  "bosch-series-8-induction": {
    emoji: "🍳",
    company: "Bosch Home",
    model: "Added 2h ago",
    docs: 6,
    sessions: 2104,
    resolutionRate: 91,
    manufacturer: "Bosch Home Appliances",
    year: "2023 - Present",
    productType: "Induction Cooktop",
  },
  "siemens-s7-1200-plc": {
    emoji: "🔧",
    company: "Siemens AG",
    model: "Added 5h ago",
    docs: 18,
    sessions: 1311,
    resolutionRate: 86,
    manufacturer: "Siemens AG",
    year: "2022 - Present",
    productType: "Programmable Logic Controller",
  },
  "ford-f-150-2023-raptor": {
    emoji: "🚗",
    company: "Ford Motor Co",
    model: "Added 1d ago",
    docs: 32,
    sessions: 5770,
    resolutionRate: 82,
    manufacturer: "Ford Motor Co",
    year: "2023",
    productType: "Performance Pickup Truck",
  },
  "moss-router-x1": {
    emoji: "📡",
    company: "Moss Labs",
    model: "Sample product",
    docs: 5,
    sessions: 642,
    resolutionRate: 88,
    manufacturer: "Moss Labs",
    year: "2024 - Present",
    productType: "Mesh Router",
  },
  "aero-clean-500": {
    emoji: "🌬️",
    company: "AeroClean",
    model: "Sample product",
    docs: 7,
    sessions: 812,
    resolutionRate: 90,
    manufacturer: "AeroClean",
    year: "2024 - Present",
    productType: "Smart Air Purifier",
  },
  "thermopro-2": {
    emoji: "🌡️",
    company: "ThermoPro",
    model: "Sample product",
    docs: 4,
    sessions: 377,
    resolutionRate: 85,
    manufacturer: "ThermoPro",
    year: "2024 - Present",
    productType: "Wireless Temperature Sensor",
  },
};

export const fallbackProducts: Product[] = [
  {
    id: "hp-laserjet-pro-m404n",
    name: "HP LaserJet Pro M404n",
    category: "Electronics",
    description:
      "A high-speed monochrome laser printer designed for small to medium workgroups. Supports USB 2.0 and Gigabit Ethernet connectivity. Rated for 80,000 pages/month duty cycle.",
    image_url: "",
  },
  {
    id: "daikin-ftxm35tvma",
    name: "Daikin FTXM35TVMA",
    category: "HVAC",
    description:
      "Wall mounted split air conditioner with inverter controls, humidity management, and service diagnostics.",
    image_url: "",
  },
  {
    id: "caterpillar-320-gc",
    name: "Caterpillar 320 GC",
    category: "Industrial",
    description:
      "Hydraulic excavator with electronic monitoring, fault codes, and planned maintenance documentation.",
    image_url: "",
  },
  {
    id: "bosch-series-8-induction",
    name: "Bosch Series 8 Induction",
    category: "Appliances",
    description:
      "Premium induction cooktop with touch controls, power management, and safety lock diagnostics.",
    image_url: "",
  },
  {
    id: "siemens-s7-1200-plc",
    name: "Siemens S7-1200 PLC",
    category: "Industrial",
    description:
      "Compact industrial PLC for automation systems with hardware diagnostics and module status references.",
    image_url: "",
  },
  {
    id: "ford-f-150-2023-raptor",
    name: "Ford F-150 2023 Raptor",
    category: "Automotive",
    description:
      "Performance pickup with service manuals, drivetrain diagnostics, and maintenance procedures.",
    image_url: "",
  },
];

export const categories = [
  "All",
  "Industrial",
  "Appliances",
  "Electronics",
  "Automotive",
  "HVAC",
];

export const commonIssues = [
  "Paper jam",
  "Faded print",
  "Network offline",
  "Toner low error",
  "Print spooler stuck",
];

export const documentation = [
  { icon: "📘", name: "User Guide & Quick Reference", meta: "PDF · 148 pages · Indexed" },
  { icon: "🔧", name: "HP Service & Repair Manual", meta: "PDF · 312 pages · Indexed", featured: true },
  { icon: "🎬", name: "Paper Jam Troubleshooting (Video)", meta: "MP4 · 8 min · Indexed" },
  { icon: "🌐", name: "HP Support Knowledge Base", meta: "URL · 2,400 articles · Indexed" },
];

export function toProductView(product: Product): ProductView {
  const meta = metaById[product.id] ?? {
    emoji: product.category.toLowerCase().includes("network")
      ? "📡"
      : product.category.toLowerCase().includes("sensor")
        ? "🌡️"
        : "⚙️",
    company: product.category,
    model: "Indexed product",
    docs: 6,
    sessions: 300,
    resolutionRate: 86,
    manufacturer: product.category,
    year: "2024 - Present",
    productType: product.category,
  };

  return {
    ...product,
    ...meta,
  };
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}
