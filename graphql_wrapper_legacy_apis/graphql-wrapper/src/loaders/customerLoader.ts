import DataLoader from "dataloader";
import { LegacyClient, LegacyCustomer } from "../datasources/legacyClient.js";

export function buildCustomerLoader(client: LegacyClient, auth?: string) {
  return new DataLoader<string, LegacyCustomer | null>(async (ids) => {
    const unique = Array.from(new Set(ids));
    const rows = await client.getCustomersBatch(unique, auth);
    const byId = new Map(rows.map((c) => [c.customer_id, c]));
    return ids.map((id) => byId.get(id) || null);
  });
}
