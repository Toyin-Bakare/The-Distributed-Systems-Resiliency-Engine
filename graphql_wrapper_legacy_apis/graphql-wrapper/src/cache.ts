import { LRUCache } from "lru-cache";

export interface Cache {
  get<T>(key: string): T | undefined;
  set<T>(key: string, value: T, ttlSeconds: number): void;
}

export class InMemoryCache implements Cache {
  private cache = new LRUCache<string, any>({ max: 5000 });

  get<T>(key: string): T | undefined {
    return this.cache.get(key) as T | undefined;
  }

  set<T>(key: string, value: T, ttlSeconds: number): void {
    this.cache.set(key, value, { ttl: ttlSeconds * 1000 });
  }
}

/** Stub you can replace with ioredis-based distributed cache. */
export class RedisCacheStub implements Cache {
  get<T>(_key: string): T | undefined { return undefined; }
  set<T>(_key: string, _value: T, _ttlSeconds: number): void {}
}
