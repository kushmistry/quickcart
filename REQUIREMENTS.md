# QuickCart — Project Requirements Document

## 1. Purpose

A hands-on learning project to understand **Kafka's real-world value** by
building the *same* e-commerce order system twice — once without Kafka
(synchronous) and once with Kafka (event-driven) — then measuring the
difference under load instead of just reading theory.

---

## 2. Problem Statement

QuickCart is an online store. When a customer places an order, the backend
currently (conceptually) does all of this **in a single request**:

1. Save the order to the database
2. Reduce stock (Inventory)
3. Charge the customer (Payment) — *out of scope for this project, simulated only*
4. Send a confirmation email (Email)
5. Log the sale (Analytics)
6. Create a shipping label (Shipping) — *optional stretch goal*

### Pain points this causes
- **Slow checkout** — the customer waits for every downstream step to finish
- **Fragile chain** — one slow/broken service (e.g. Email) fails the whole order
- **Can't scale independently** — Analytics/Email are forced to keep up with
  Order volume in real time even though they don't need to
- **No replay** — if a service is down when the order happens, that event is
  simply lost
- **Tight coupling** — Order Service must directly know about and call every
  other service

### Goal
Prove — with real numbers, not just theory — that an event-driven design
(Kafka) solves these problems, and understand *why* and *by how much*.

---

## 3. Scope

### In scope
- Order creation API (FastAPI)
- Real relational database (PostgreSQL)
- Two architectural versions of the same system:
  - **Version A** — synchronous, direct function calls, no Kafka
  - **Version B** — event-driven, Kafka `order_created` topic + independent consumers
- Simulated downstream services: Inventory, Email (deliberately slow),
  Analytics
- Load testing both versions with concurrent dummy users
- Fault-injection test: simulate a slow/down service and observe impact
- Side-by-side comparison of measured results

### Out of scope (for this learning project)
- Real payment processing
- Real email delivery (SMTP) — printed/logged instead
- Authentication/authorization
- Frontend UI
- Production-grade deployment (Kubernetes, CI/CD, etc.)
- Kafka Connect / Schema Registry / Avro (mentioned only as future learning)

---

## 4. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| API framework | FastAPI | async-native, lightweight, good fit for microservices |
| Database | PostgreSQL (via Docker) | real DB, not SQLite, to feel closer to production |
| ORM | SQLAlchemy | |
| Message broker | Apache Kafka (via Docker, KRaft mode) | no Zookeeper needed |
| Kafka client | `confluent-kafka` (Python) | fast, well-maintained |
| Load testing | Locust or a custom `asyncio`/`httpx` script | simulate concurrent dummy users |
| Containerization | Docker + Docker Compose | Postgres + Kafka run as services |

---

## 5. Functional Requirements

### 5.1 Order Service (API) — shared by both versions
- `POST /orders` — create a new order
  - Input: `customer_name`, `item`, `quantity`, `price`
  - Saves order to PostgreSQL with status `created`
- `GET /orders` — list all orders
- `GET /orders/{id}` — fetch a single order
- `GET /health` — basic health check

### 5.2 Version A — Synchronous
- `POST /orders` additionally, **inline, before responding**:
  - Calls Inventory logic directly (reduce stock)
  - Calls Email logic directly (simulated with an artificial delay)
  - Calls Analytics logic directly (log the sale)
- If any step is slow, the whole API response is delayed
- If any step throws an error, the whole order request fails

### 5.3 Version B — Event-driven (Kafka)
- `POST /orders`:
  - Saves order to PostgreSQL
  - Publishes an `order_created` event to Kafka topic `orders`
  - Returns response immediately — does **not** wait for downstream services
- Independent consumer processes, each in a Kafka consumer group:
  - `inventory_consumer.py` — reduces stock
  - `email_consumer.py` — simulates sending email (same artificial delay as Version A, but doesn't block the API)
  - `analytics_consumer.py` — logs sale stats
- Consumers can be stopped/restarted independently without affecting the API
  or other consumers

---

## 6. Non-Functional Requirements / What We're Measuring

| Metric | How it's tested |
|---|---|
| API response time per order | Timed on every `POST /orders` call, both versions |
| Throughput under load | N concurrent dummy users placing orders over a fixed window |
| Impact of a slow downstream service | Add artificial delay to Email step, compare API latency in A vs B |
| Behavior when a service is down | Kill Email consumer mid-test in Version B; kill Email logic path in Version A (simulate exception) |
| Recovery / replay | Restart a killed Kafka consumer and confirm it catches up on missed events; confirm Version A has no equivalent recovery |
| Resource behavior under spike | Sudden burst of orders ("flash sale" simulation), observe latency curve |

---

## 7. Success Criteria (what "done" looks like)

- [ ] Version A fully working and load-tested, with baseline numbers recorded
- [ ] Version B fully working and load-tested, with comparable numbers recorded
- [ ] A clear before/after comparison (response time, failure behavior, recovery)
- [ ] Demonstrated: killing the Email consumer in Version B does **not** affect
      order creation or other consumers
- [ ] Demonstrated: Kafka retains and allows replay of missed events after a
      consumer restart
- [ ] Personal understanding of: topics, partitions, producers, consumers,
      consumer groups, offsets — gained by direct experimentation, not just
      reading

---

## 8. Project Structure (planned, will grow)

```
quickcart/
├── docker-compose.yml          # Postgres (+ Kafka added later)
├── requirements.txt
├── .env
├── README.md
├── REQUIREMENTS.md             # this file
└── app/
    ├── database.py
    ├── models.py
    ├── schemas.py
    └── main.py                 # will branch into version_a / version_b logic
```

(Consumer scripts and load-testing scripts will be added as separate files
once Kafka is introduced.)

---

## 9. Build Order (roadmap)

1. ✅ FastAPI + PostgreSQL base setup (done)
2. Add Version A synchronous downstream logic (Inventory/Email/Analytics as
   direct calls)
3. Load test Version A, record baseline numbers
4. Add Kafka via Docker Compose
5. Build Version B: producer changes + 3 independent consumer scripts
6. Load test Version B the same way, record numbers
7. Fault-injection tests (kill/restart a consumer) on Version B
8. Write up the comparison — the actual "why Kafka" proof, backed by data
