import { LegacyClient } from "./datasources/legacyClient.js";
import { Cache, InMemoryCache } from "./cache.js";
import { buildCustomerLoader } from "./loaders/customerLoader.js";
import { buildOrderLoader } from "./loaders/orderLoader.js";

export type GraphQLContext = {
  requestId: string;
  auth?: string;
  legacy: LegacyClient;
  cache: Cache;
  loaders: {
    customerById: ReturnType<typeof buildCustomerLoader>;
    orderById: ReturnType<typeof buildOrderLoader>;
  };
};

export function buildContext(opts: {
  requestId: string;
  auth?: string;
  legacyBaseUrl: string;
  cache?: Cache;
}): GraphQLContext {
  const legacy = new LegacyClient(opts.legacyBaseUrl);
  const cache = opts.cache ?? new InMemoryCache();

  return {
    requestId: opts.requestId,
    auth: opts.auth,
    legacy,
    cache,
    loaders: {
      customerById: buildCustomerLoader(legacy, opts.auth),
      orderById: buildOrderLoader(legacy, opts.auth),
    },
  };
}
