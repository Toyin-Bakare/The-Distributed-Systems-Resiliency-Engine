from __future__ import annotations
import argparse, asyncio, time, random
import httpx

async def worker(client: httpx.AsyncClient, base_url: str, stop_at: float, stats: dict):
    while time.time() < stop_at:
        path = random.choice(["/v1/hello", "/v1/hello", "/v1/hello", "/v1/downstream", "/v1/error"])
        try:
            r = await client.get(base_url + path, timeout=2.5)
            if r.status_code == 200:
                stats["ok"] += 1
            else:
                stats["bad"] += 1
        except Exception:
            stats["errors"] += 1

async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", required=True)
    p.add_argument("--seconds", type=int, default=10)
    p.add_argument("--concurrency", type=int, default=10)
    args = p.parse_args()

    stats = {"ok": 0, "bad": 0, "errors": 0}
    stop_at = time.time() + args.seconds

    async with httpx.AsyncClient() as client:
        tasks = [asyncio.create_task(worker(client, args.base_url, stop_at, stats)) for _ in range(args.concurrency)]
        await asyncio.gather(*tasks)

    print(stats)

if __name__ == "__main__":
    asyncio.run(main())
