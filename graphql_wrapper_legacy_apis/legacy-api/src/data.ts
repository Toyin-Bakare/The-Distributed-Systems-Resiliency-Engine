export type Customer = {
  id: string;
  name: string;
  email: string;
  tier: "FREE" | "PRO" | "ENT";
};

export type Order = {
  id: string;
  customerId: string;
  status: "NEW" | "PAID" | "CANCELED";
  total: number;
  createdAt: string;
};

export const customers: Customer[] = [
  { id: "c-001", name: "Ada Okafor", email: "ada@example.com", tier: "PRO" },
  { id: "c-002", name: "Bola Adeyemi", email: "bola@example.com", tier: "FREE" },
  { id: "c-003", name: "Chidi Nwosu", email: "chidi@example.com", tier: "ENT" },
];

export const orders: Order[] = [
  { id: "o-100", customerId: "c-001", status: "PAID", total: 199.0, createdAt: new Date(Date.now()-86400000).toISOString() },
  { id: "o-101", customerId: "c-001", status: "NEW", total: 49.0, createdAt: new Date().toISOString() },
  { id: "o-200", customerId: "c-002", status: "CANCELED", total: 20.0, createdAt: new Date(Date.now()-3600000).toISOString() },
  { id: "o-300", customerId: "c-003", status: "PAID", total: 999.0, createdAt: new Date(Date.now()-7200000).toISOString() },
];
