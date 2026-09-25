# 🛒 QuickCart — Synchronous vs. Event-Driven (Kafka) Benchmark

An empirical benchmark demonstrating the architectural value of **Apache Kafka** by building the exact same e-commerce order processing system twice:
1. **Version A (Synchronous)**: Direct blocking function calls in a monolithic request cycle.
2. **Version B (Event-Driven)**: Asynchronous event streaming using Apache Kafka (KRaft mode) and independent consumer groups.

---

## 📊 The Empirical Proof (Benchmark Results)

We subjected both architectures to the exact same workload: **50 orders placed across 10 concurrent shoppers**.

| Metric | Version A (Synchronous) | Version B (Kafka Event-Driven) | Impact |
|:---|:---:|:---:|:---:|
| **Total Test Duration** | **7.76 s** | **0.27 s** | **28.7x Faster** ⚡ |
| **Throughput (RPS)** | **6.44 orders/sec** | **188.67 orders/sec** | **+2,830% (+29.3x)** 📈 |
| **Average Latency** | **1,536 ms** (1.53s) | **37.6 ms** (0.037s) | **97.5% Reduction** ⏱️ |
| **Median (P50) Latency**| **1,522 ms** | **31.4 ms** | **98.0% Faster** |
| **P95 Latency** | **1,602 ms** | **73.9 ms** | **95.4% Faster** |
| **Failure Tolerance** | ❌ Downstream crash fails the order | ✅ Zero impact on checkout | **Resilient** 🛡️ |
| **Replay & Catch-Up** | ❌ None (lost data) | ✅ Automatic offset replay | **Zero Data Loss** |

---

## 🏛️ Architecture Comparison

### Version A: Synchronous (Tight Coupling & Blocking)
Every customer must wait for all downstream operations before receiving an HTTP response:
```
[Customer] ──POST /orders──▶ [Order API]
                                  │
                                  ├─▶ 1. Save to PostgreSQL (~30ms)
                                  ├─▶ 2. Inventory Deduction (~1ms)
                                  ├─▶ 3. Email Provider (~1,500ms delay) ⚠️ BOTTLENECK
                                  └─▶ 4. Analytics Logging (~1ms)
                                  │
[Customer] ◀──201 Created (1.53s)─┘
```
- **Pain Points**: High latency, slow throughput, and catastrophic failure cascades (if the email service fails, checkout fails).

---

### Version B: Event-Driven with Kafka (Loose Coupling & Non-Blocking)
The API persists the order, publishes an `order_created` event to Kafka in $< 2$ms, and returns immediately:
```
[Customer] ──POST /orders──▶ [Order API] ──▶ Save to DB (~30ms)
                                  │
                                  ├──▶ Publish Event to Kafka (< 2ms)
                                  │
[Customer] ◀──201 Created (31ms)──┘
                                  │
                   ┌──────────────┴──────────────┐
                   │     Kafka Topic: orders     │
                   └──────────────┬──────────────┘
                                  │ (Fan-out to independent Consumer Groups)
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│ inventory-group   │   │ email-group       │   │ analytics-group   │
│ (Inventory Worker)│   │ (Email Worker)    │   │ (Analytics Worker)│
│ Processes instantly│  │ Processes slowly  │   │ Logs data in real-time
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

---

## 🛡️ Fault Tolerance & Recovery (Chaos Test)

During load testing on **Version B**, the `email_consumer` process was killed (`SIGINT`) mid-traffic to simulate a third-party email provider outage:
1. **Checkout was completely unaffected**: The API continued processing orders with ~30ms latency.
2. **Other services remained operational**: The `inventory_consumer` and `analytics_consumer` continued processing orders uninterrupted.
3. **Automatic Replay on Recovery**: When `email_consumer` was restarted, it read its committed consumer offset from Kafka and sequentially caught up on every missed email with **zero dropped events**.

---

## 🛠️ Tech Stack

- **API**: FastAPI, Uvicorn (ASGI)
- **Database**: PostgreSQL 16 (via Docker)
- **ORM & Migrations**: SQLAlchemy 2.0, Alembic
- **Event Streaming**: Apache Kafka (KRaft mode — ZooKeeper-less)
- **Kafka Client**: `confluent-kafka` (Python)
- **Settings**: Pydantic v2 `BaseSettings`
- **Benchmarking**: `httpx`, `asyncio`

---

## 🚀 Getting Started

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.10+

### 2. Environment Setup
```bash
git clone https://github.com/<YOUR_USERNAME>/quickcart.git
cd quickcart

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Start PostgreSQL & Kafka
```bash
docker compose up -d
docker compose ps
```

### 4. Run Migrations
```bash
alembic upgrade head
```

### 5. Start the API
```bash
uvicorn app.main:app --reload --port 8001
```
Interactive API docs available at `http://localhost:8001/docs`.

---

## 🔬 Reproducing the Benchmark

### Test Version A (Synchronous)
1. In `.env`, set `USE_KAFKA=False`.
2. Run the benchmark:
   ```bash
   python benchmark.py
   ```

### Test Version B (Kafka Event-Driven)
1. In `.env`, set `USE_KAFKA=True`.
2. Start the 3 consumer workers in separate terminals:
   ```bash
   python -m app.consumers.inventory_consumer
   python -m app.consumers.email_consumer
   python -m app.consumers.analytics_consumer
   ```
3. Run the benchmark:
   ```bash
   python benchmark.py
   ```

---

## 💡 Key Architectural Takeaways

- **Decoupling**: The order service doesn't know or care who consumes the order event. New services (like Shipping or Fraud Detection) can be added with zero changes to the core checkout API.
- **Backpressure & Shock Absorption**: Slow downstream services process messages at their own sustainable rate without degrading customer response times.
- **Consumer Groups**: Each service group gets its own independent stream of events, allowing horizontal scalability by simply adding more worker instances to the group.

