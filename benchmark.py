import asyncio
import time
import statistics
import httpx

from app.settings import settings

# Read dynamically from settings / .env
API_URL = f"{settings.API_BASE_URL}/orders"
TOTAL_ORDERS = settings.BENCHMARK_TOTAL_ORDERS
CONCURRENCY = settings.BENCHMARK_CONCURRENCY

async def send_order(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, order_idx: int) -> tuple[bool, float]:
    payload = {
        "customer_name": f"Customer_{order_idx}",
        "item": "Mechanical Keyboard",
        "quantity": 1,
        "price": 79.99
    }
    
    async with semaphore:
        start_time = time.perf_counter()
        try:
            response = await client.post(API_URL, json=payload, timeout=10.0)
            latency = time.perf_counter() - start_time
            success = (response.status_code == 201)
            return success, latency
        except Exception:
            latency = time.perf_counter() - start_time
            return False, latency

async def run_benchmark():
    print(f"\n=======================================================")
    print(f"🚀 Running Benchmark: {TOTAL_ORDERS} orders with {CONCURRENCY} concurrent workers")
    print(f"Target: {API_URL}")
    print(f"=======================================================\n")

    semaphore = asyncio.Semaphore(CONCURRENCY)
    limits = httpx.Limits(max_connections=CONCURRENCY, max_keepalive_connections=CONCURRENCY)
    
    overall_start = time.perf_counter()
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [send_order(client, semaphore, i) for i in range(1, TOTAL_ORDERS + 1)]
        results = await asyncio.gather(*tasks)
    
    total_time = time.perf_counter() - overall_start

    latencies = [lat for success, lat in results if success]
    successful_requests = len(latencies)
    failed_requests = TOTAL_ORDERS - successful_requests
    rps = successful_requests / total_time if total_time > 0 else 0

    print("-------------------- RESULTS --------------------")
    print(f"Total Requests:       {TOTAL_ORDERS}")
    print(f"Successful (201):     {successful_requests}")
    print(f"Failed:               {failed_requests}")
    print(f"Total Elapsed Time:   {total_time:.2f} s")
    print(f"Throughput (RPS):     {rps:.2f} orders/sec")
    print("------------------ LATENCY (sec) -----------------")
    if latencies:
        print(f"Min Latency:          {min(latencies):.4f} s")
        print(f"Max Latency:          {max(latencies):.4f} s")
        print(f"Average Latency:      {statistics.mean(latencies):.4f} s")
        print(f"Median (P50):         {statistics.median(latencies):.4f} s")
        sorted_latencies = sorted(latencies)
        p95_idx = int(len(sorted_latencies) * 0.95)
        print(f"P95 Latency:          {sorted_latencies[p95_idx]:.4f} s")
    print("=================================================\n")

if __name__ == "__main__":
    asyncio.run(run_benchmark())