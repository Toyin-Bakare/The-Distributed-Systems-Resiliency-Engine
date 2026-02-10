from __future__ import annotations
import argparse, asyncio, time
import httpx

async def worker(client: httpx.AsyncClient, url: str, api_key: str | None, stop_at: float, stats: dict):
    while time.time() < stop_at:
        headers = {}
        if api_key:
            headers["x-api-key"] = api_key
        try:
            r = await client.get(url, headers=headers, timeout=2.5)
            if r.status_code == 200:
                stats["ok"] += 1
            elif r.status_code == 429:
                stats["throttled"] += 1
            else:
                stats["other"] += 1
        except Exception:
            stats["errors"] += 1

async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--api-key", default=None)
    p.add_argument("--concurrency", type=int, default=20)
    p.add_argument("--seconds", type=int, default=10)
    args = p.parse_args()

    stats = {"ok": 0, "throttled": 0, "other": 0, "errors": 0}
    stop_at = time.time() + args.seconds

    async with httpx.AsyncClient() as client:
        tasks = [asyncio.create_task(worker(client, args.url, args.api_key, stop_at, stats)) for _ in range(args.concurrency)]
        await asyncio.gather(*tasks)

    total = sum(stats.values())
    print({"total": total, **stats})

if __name__ == "__main__":
    asyncio.run(main())
