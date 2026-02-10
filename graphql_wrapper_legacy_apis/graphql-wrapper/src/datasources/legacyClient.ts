import axios, { AxiosInstance } from "axios";

export type LegacyCustomer = {
  customer_id: string;
  full_name: string;
  email_address: string;
  tier: string;
};

export type LegacyOrderRef = { order_id: string; status?: string };

export type LegacyOrder = {
  order_id: string;
  customer_id: string;
  status: string;
  total_amount: number;
  created_at: string;
};

export class LegacyClient {
  private http: AxiosInstance;

  constructor(private baseUrl: string) {
    this.http = axios.create({ baseURL: baseUrl, timeout: 2500 });
  }

  private async withRetry<T>(fn: () => Promise<T>, maxRetries = 2): Promise<T> {
    let lastErr: any;
    for (let i = 0; i <= maxRetries; i++) {
      try {
        return await fn();
      } catch (e: any) {
        lastErr = e;
        const status = e?.response?.status;
        if (i < maxRetries && (!status || status >= 500)) {
          await new Promise((r) => setTimeout(r, 80 * (i + 1)));
          continue;
        }
        throw e;
      }
    }
    throw lastErr;
  }

  async getCustomer(id: string, auth?: string) {
    return this.withRetry(async () => {
      const res = await this.http.get(`/customers/${encodeURIComponent(id)}`, {
        headers: auth ? { authorization: auth } : undefined,
      });
      return res.data as LegacyCustomer;
    });
  }

  async getCustomersBatch(ids: string[], auth?: string) {
    const qs = ids.map(encodeURIComponent).join(",");
    return this.withRetry(async () => {
      const res = await this.http.get(`/customers`, {
        params: { ids: qs },
        headers: auth ? { authorization: auth } : undefined,
      });
      return (res.data?.rows || []) as LegacyCustomer[];
    });
  }

  async getCustomerOrders(customerId: string, auth?: string) {
    return this.withRetry(async () => {
      const res = await this.http.get(`/customers/${encodeURIComponent(customerId)}/orders`, {
        headers: auth ? { authorization: auth } : undefined,
      });
      return (res.data?.orders || []) as LegacyOrderRef[];
    });
  }

  async getOrder(orderId: string, auth?: string) {
    return this.withRetry(async () => {
      const res = await this.http.get(`/orders/${encodeURIComponent(orderId)}`, {
        headers: auth ? { authorization: auth } : undefined,
      });
      return res.data as LegacyOrder;
    });
  }
}
