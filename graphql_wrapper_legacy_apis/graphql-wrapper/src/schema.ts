import { gql } from "graphql-tag";

export const typeDefs = gql`
  type Customer {
    id: ID!
    name: String!
    email: String!
    tier: String!
    orders: [Order!]!
  }

  type Order {
    id: ID!
    status: String!
    total: Float!
    createdAt: String!
    customer: Customer!
  }

  type Query {
    customer(id: ID!): Customer
    customers(ids: [ID!]!): [Customer!]!
    order(id: ID!): Order
  }
`;
