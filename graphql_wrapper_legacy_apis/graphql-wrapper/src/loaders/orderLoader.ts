import DataLoader from "dataloader";
import { LegacyClient, LegacyOrder } from "../datasources/legacyClient.js";

/**
 * Even without a batch endpoint, DataLoader still helps:
 * - dedup repeated lookups within a request
 * - centralizes error handling for missing orders
 */
export function buildOrderLoader(client: LegacyClient, auth?: string) {
  return new DataLoader<string, LegacyOrder | null>(async (orderIds) => {
    const out: (LegacyOrder | null)[] = [];
    for (const id of orderIds) {
      try {
        out.push(await client.getOrder(id, auth));
      } catch {
        out.push(null);
      }
    }
    return out;
  });
}
