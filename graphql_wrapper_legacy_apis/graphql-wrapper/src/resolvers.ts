import { GraphQLContext } from "./context.js";

function mapCustomer(c: any) {
  return { id: c.customer_id, name: c.full_name, email: c.email_address, tier: c.tier };
}

function mapOrder(o: any) {
  return {
    id: o.order_id,
    status: o.status,
    total: o.total_amount,
    createdAt: o.created_at,
    customerId: o.customer_id,
  };
}

export const resolvers = {
  Query: {
    customer: async (_: any, args: { id: string }, ctx: GraphQLContext) => {
      const cacheKey = `customer:${args.id}`;
      const cached = ctx.cache.get<any>(cacheKey);
      if (cached) return cached;

      const c = await ctx.legacy.getCustomer(args.id, ctx.auth);
      const mapped = mapCustomer(c);
      ctx.cache.set(cacheKey, mapped, 30);
      return mapped;
    },

    customers: async (_: any, args: { ids: string[] }, ctx: GraphQLContext) => {
      const rows = await ctx.legacy.getCustomersBatch(args.ids, ctx.auth);
      return rows.map(mapCustomer);
    },

    order: async (_: any, args: { id: string }, ctx: GraphQLContext) => {
      const o = await ctx.legacy.getOrder(args.id, ctx.auth);
      return mapOrder(o);
    },
  },

  Customer: {
    orders: async (parent: any, _args: any, ctx: GraphQLContext) => {
      const refs = await ctx.legacy.getCustomerOrders(parent.id, ctx.auth);
      const orders = await Promise.all(refs.map((r: any) => ctx.loaders.orderById.load(r.order_id)));
      return orders.filter(Boolean).map(mapOrder);
    },
  },

  Order: {
    customer: async (parent: any, _args: any, ctx: GraphQLContext) => {
      const c = await ctx.loaders.customerById.load(parent.customerId);
      if (!c) return null;
      return mapCustomer(c);
    },
  },
};
