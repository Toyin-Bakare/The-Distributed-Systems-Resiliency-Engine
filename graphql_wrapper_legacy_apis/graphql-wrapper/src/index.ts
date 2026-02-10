import { createApp } from "./server.js";

const PORT = Number(process.env.PORT || 4000);

async function main() {
  const app = await createApp();
  app.listen(PORT, () => {
    console.log(`[graphql-wrapper] listening on :${PORT} (GraphQL at /graphql)`);
  });
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
