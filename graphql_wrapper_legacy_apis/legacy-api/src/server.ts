import express from "express";
import morgan from "morgan";
import { customers, orders } from "./data.js";

const app = express();
app.use(express.json());
app.use(morgan("dev"));

const PORT = Number(process.env.PORT || 4001);

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}
async function maybeDelay() {
  const ms = 40 + Math.floor(Math.random() * 120);
  await sleep(ms);
}

app.use((req, res, next) => {
  if (req.path === "/health") return next();
  const auth = req.header("authorization");
  res.setHeader("x-legacy-auth-seen", auth ? "1" : "0");
  next();
});

app.get("/health", (_req, res) => res.json({ ok: true }));

app.get("/customers/:id", async (req, res) => {
  await maybeDelay();
  const c = customers.find((x) => x.id === req.params.id);
  if (!c) return res.status(404).json({ error: "not_found" });
  return res.json({ customer_id: c.id, full_name: c.name, email_address: c.email, tier: c.tier });
});

app.get("/customers", async (req, res) => {
  await maybeDelay();
  const ids = String(req.query.ids || "").split(",").filter(Boolean);
  const rows = customers.filter((c) => ids.includes(c.id)).map((c) => ({
    customer_id: c.id,
    full_name: c.name,
    email_address: c.email,
    tier: c.tier,
  }));
  return res.json({ rows });
});

app.get("/customers/:id/orders", async (req, res) => {
  await maybeDelay();
  const rows = orders.filter((o) => o.customerId === req.params.id).map((o) => ({
    order_id: o.id,
    status: o.status,
  }));
  return res.json({ customer_id: req.params.id, orders: rows });
});

app.get("/orders/:id", async (req, res) => {
  await maybeDelay();
  const o = orders.find((x) => x.id === req.params.id);
  if (!o) return res.status(404).json({ error: "not_found" });
  return res.json({
    order_id: o.id,
    customer_id: o.customerId,
    status: o.status,
    total_amount: o.total,
    created_at: o.createdAt,
  });
});

app.listen(PORT, () => console.log(`[legacy-api] listening on :${PORT}`));
