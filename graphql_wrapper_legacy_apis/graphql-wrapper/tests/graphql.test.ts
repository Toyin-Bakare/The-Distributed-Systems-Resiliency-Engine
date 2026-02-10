import { describe, it, expect, beforeAll, afterAll } from "vitest";
import request from "supertest";
import { createApp } from "../src/server.js";

let server: any;

describe("GraphQL wrapper integration", () => {
  beforeAll(async () => {
    // NOTE: This test assumes the legacy API is running at localhost:4001
    process.env.LEGACY_BASE_URL = process.env.LEGACY_BASE_URL || "http://localhost:4001";
    const app = await createApp();
    server = app.listen(0);
  });

  afterAll(async () => {
    await new Promise<void>((resolve) => server.close(() => resolve()));
  });

  it("fetches customer with orders", async () => {
    const body = {
      query: `query Demo($id: ID!) {
        customer(id: $id) {
          id name email tier
          orders { id status total createdAt customer { id name } }
        }
      }`,
      variables: { id: "c-001" },
    };

    const res = await request(server).post("/graphql").send(body);
    expect(res.status).toBe(200);
    expect(res.body.data.customer.id).toBe("c-001");
    expect(Array.isArray(res.body.data.customer.orders)).toBe(true);
  });
});
