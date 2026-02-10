import express from "express";
import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@apollo/server/express4";
import { makeExecutableSchema } from "@graphql-tools/schema";
import { typeDefs } from "./schema.js";
import { resolvers } from "./resolvers.js";
import { buildContext } from "./context.js";
import { randomUUID } from "crypto";

export async function createApp() {
  const app = express();
  app.use(express.json({ limit: "1mb" }));

  const schema = makeExecutableSchema({ typeDefs, resolvers });
  const server = new ApolloServer({ schema });
  await server.start();

  const legacyBaseUrl = process.env.LEGACY_BASE_URL || "http://localhost:4001";

  app.get("/health", (_req, res) => res.json({ ok: true }));

  app.use("/graphql", (req, res, next) => {
    const requestId = (req.header("x-request-id") || randomUUID()) as string;
    (req as any).__requestId = requestId;
    res.setHeader("x-request-id", requestId);
    next();
  });

  app.use(
    "/graphql",
    expressMiddleware(server, {
      context: async ({ req }) => {
        const requestId = (req as any).__requestId as string;
        const auth = req.headers["authorization"] as string | undefined;
        return buildContext({ requestId, auth, legacyBaseUrl });
      },
    })
  );

  return app;
}
