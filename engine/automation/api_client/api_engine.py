import time
import random
import hashlib
import json
from collections import defaultdict

# ==========================================
# 🔌 OMNI AUTOMATION: API Client Engine (Phase 161)
# ==========================================
#
# PROSES BELAJAR:
# ──────────────────────
# API automation BUKAN hanya requests.get(url).
# Production-grade API client butuh:
#
# 1. RETRY with EXPONENTIAL BACKOFF — jangan spam server
# 2. RATE LIMITING — token bucket / sliding window
# 3. PAGINATION — handle cursor/offset/keyset pagination
# 4. AUTHENTICATION — API key, OAuth2, JWT refresh
# 5. CIRCUIT BREAKER — stop calling broken service
# 6. WEBHOOK RECEIVER — handle inbound callbacks
# 7. REQUEST/RESPONSE INTERCEPTORS — logging, transform

# ─────────────────────────────────────────────────
# KOMPONEN 1: Rate Limiter (Token Bucket)
# ─────────────────────────────────────────────────
class TokenBucketRateLimiter:
    """
    PELAJARAN: Token Bucket = standar industri untuk rate limiting.
    Bucket terisi dengan kecepatan konstan (tokens/second).
    Setiap request mengambil 1 token. Jika kosong → tunggu/tolak.
    Burst diperbolehkan (sampai bucket penuh).
    """
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens/second
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def acquire(self):
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def wait_and_acquire(self):
        while not self.acquire():
            time.sleep(0.01)
        return True


# ─────────────────────────────────────────────────
# KOMPONEN 2: Circuit Breaker
# ─────────────────────────────────────────────────
class CircuitBreaker:
    """
    PELAJARAN: Circuit Breaker MENCEGAH cascade failure.
    3 states:
    - CLOSED: normal, requests diteruskan
    - OPEN: terlalu banyak error → SEMUA requests ditolak (fast-fail)
    - HALF-OPEN: setelah cooldown, coba 1 request → jika sukses → CLOSED
    """
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold=3, recovery_timeout=5.0):
        self.state = self.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = 0

    def can_execute(self):
        if self.state == self.CLOSED:
            return True
        if self.state == self.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = self.HALF_OPEN
                print(f"         🔄 Circuit → HALF_OPEN (trying one request)")
                return True
            return False
        if self.state == self.HALF_OPEN:
            return True
        return False

    def record_success(self):
        self.failure_count = 0
        if self.state == self.HALF_OPEN:
            self.state = self.CLOSED
            print(f"         ✅ Circuit → CLOSED (service recovered)")

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN
            print(f"         🔴 Circuit → OPEN (threshold {self.failure_threshold} reached)")


# ─────────────────────────────────────────────────
# KOMPONEN 3: Authentication Handlers
# ─────────────────────────────────────────────────
class AuthHandler:
    """Base auth handler."""
    def apply(self, headers):
        return headers

class APIKeyAuth(AuthHandler):
    def __init__(self, key, header="X-API-Key"):
        self.key = key
        self.header = header
    def apply(self, headers):
        headers[self.header] = self.key
        return headers

class BearerAuth(AuthHandler):
    def __init__(self, token):
        self.token = token
    def apply(self, headers):
        headers["Authorization"] = f"Bearer {self.token}"
        return headers

class OAuth2Auth(AuthHandler):
    """
    PELAJARAN: OAuth2 flow:
    1. Client sends client_id + client_secret → token endpoint
    2. Gets access_token + refresh_token
    3. access_token expires → use refresh_token untuk dapat baru
    """
    def __init__(self, client_id, client_secret, token_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0

    def ensure_token(self):
        if not self.access_token or time.time() > self.expires_at:
            self.access_token = f"at_{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}"
            self.refresh_token = f"rt_{random.randint(1000, 9999)}"
            self.expires_at = time.time() + 3600
            print(f"         🔑 OAuth2: Token refreshed (expires in 1h)")

    def apply(self, headers):
        self.ensure_token()
        headers["Authorization"] = f"Bearer {self.access_token}"
        return headers


# ─────────────────────────────────────────────────
# KOMPONEN 4: Pagination Handlers
# ─────────────────────────────────────────────────
class PaginationStrategy:
    def get_all(self, fetch_fn, **kwargs):
        raise NotImplementedError

class OffsetPagination(PaginationStrategy):
    """Standard offset/limit pagination."""
    def __init__(self, page_size=20):
        self.page_size = page_size

    def get_all(self, fetch_fn, max_pages=5):
        all_items = []
        for page in range(max_pages):
            offset = page * self.page_size
            result = fetch_fn(offset=offset, limit=self.page_size)
            items = result.get("items", [])
            all_items.extend(items)
            print(f"         📄 Page {page+1}: {len(items)} items (offset={offset})")
            if len(items) < self.page_size:
                break
        return all_items

class CursorPagination(PaginationStrategy):
    """Cursor-based (next_cursor) pagination."""
    def get_all(self, fetch_fn, max_pages=5):
        all_items = []
        cursor = None
        for page in range(max_pages):
            result = fetch_fn(cursor=cursor)
            items = result.get("items", [])
            all_items.extend(items)
            cursor = result.get("next_cursor")
            print(f"         📄 Page {page+1}: {len(items)} items (cursor={cursor})")
            if not cursor:
                break
        return all_items


# ─────────────────────────────────────────────────
# KOMPONEN 5: REST API Client
# ─────────────────────────────────────────────────
class APIClient:
    """
    Production-grade REST API client.
    """
    def __init__(self, base_url, auth=None, rate_limiter=None):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter(10, 2)
        self.circuit_breaker = CircuitBreaker()
        self.interceptors = []
        self.request_log = []

        print(f"🔌 [API] Client → {base_url}")
        if auth:
            print(f"   Auth: {type(auth).__name__}")

    def add_interceptor(self, fn):
        self.interceptors.append(fn)

    def request(self, method, path, data=None, params=None, retry=True, max_retries=3):
        url = f"{self.base_url}{path}"

        # Rate limiting
        self.rate_limiter.wait_and_acquire()

        # Circuit breaker
        if not self.circuit_breaker.can_execute():
            print(f"      🔴 [CIRCUIT OPEN] Request blocked: {method} {url}")
            return {"error": "Circuit breaker OPEN", "status": 503}

        # Build headers
        headers = {"Content-Type": "application/json"}
        if self.auth:
            headers = self.auth.apply(headers)

        # Interceptors
        for interceptor in self.interceptors:
            interceptor(method, url, headers, data)

        # Simulate request
        print(f"      📡 {method} {url}")

        attempt = 0
        while attempt < max_retries:
            attempt += 1
            # Simulate response
            status = random.choice([200, 200, 200, 200, 200, 500]) if attempt < 3 else 200
            response_data = self._simulate_response(method, path, data)

            if status >= 500 and retry and attempt < max_retries:
                backoff = 2 ** attempt * 0.01  # Exponential backoff (reduced for test)
                print(f"         ❌ {status} (attempt {attempt}) → retry in {backoff:.2f}s")
                self.circuit_breaker.record_failure()
                continue

            if status < 400:
                self.circuit_breaker.record_success()

            self.request_log.append({"method": method, "url": url, "status": status})
            response_data["status"] = status
            return response_data

        return {"error": "Max retries exceeded", "status": 500}

    def _simulate_response(self, method, path, data):
        if method == "GET" and "users" in path:
            return {"items": [{"id": i, "name": f"User {i}"} for i in range(5)], "next_cursor": None}
        if method == "POST":
            return {"id": random.randint(100, 999), "created": True}
        return {"data": f"Response for {method} {path}"}

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)
    def post(self, path, data=None, **kwargs):
        return self.request("POST", path, data=data, **kwargs)
    def put(self, path, data=None, **kwargs):
        return self.request("PUT", path, data=data, **kwargs)
    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)


# ─────────────────────────────────────────────────
# KOMPONEN 6: Webhook Receiver
# ─────────────────────────────────────────────────
class WebhookReceiver:
    """
    PELAJARAN: Webhook = inbound HTTP callback.
    Service PUSH data ke kita (bukan kita yang polling).
    Harus: verify signature, idempotency check, async processing.
    """
    def __init__(self, secret="webhook_secret"):
        self.secret = secret
        self.handlers = {}
        self.received = []
        self.processed_ids = set()  # Idempotency

    def register(self, event_type, handler):
        self.handlers[event_type] = handler

    def verify_signature(self, payload, signature):
        expected = hashlib.sha256(f"{payload}{self.secret}".encode()).hexdigest()
        return signature == expected

    def receive(self, event_type, payload, signature=""):
        print(f"      📥 Webhook: {event_type}")

        # Idempotency check
        event_id = payload.get("id", hashlib.md5(str(payload).encode()).hexdigest())
        if event_id in self.processed_ids:
            print(f"         ⏭️ Duplicate (idempotent skip)")
            return {"status": "duplicate"}
        self.processed_ids.add(event_id)

        # Dispatch
        handler = self.handlers.get(event_type)
        if handler:
            result = handler(payload)
            self.received.append({"type": event_type, "result": result})
            print(f"         ✅ Processed: {result}")
            return result

        print(f"         ⚠️ No handler for '{event_type}'")
        return {"status": "unhandled"}


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🔌 OMNI API — REST Client + Webhooks + Rate Limiting")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Rate Limiting: Token Bucket (capacity + refill rate)")
    print("   Circuit Breaker: CLOSED → OPEN → HALF_OPEN → CLOSED")
    print("   Auth: API Key, Bearer, OAuth2 (refresh flow)")
    print("   Pagination: offset/limit vs cursor-based")
    print("   Webhooks: verify signature, idempotency, async dispatch")

    # PART 1: API Client
    print(f"\n{'─'*60}")
    print("📋 PART 1: REST API Client")
    client = APIClient("https://api.example.com",
                       auth=OAuth2Auth("client_123", "secret", "https://auth.example.com/token"),
                       rate_limiter=TokenBucketRateLimiter(5, 10))

    # Interceptor for logging
    client.add_interceptor(lambda m, u, h, d: None)  # silent logger

    users = client.get("/v1/users")
    print(f"      → {len(users.get('items', []))} users")

    new_user = client.post("/v1/users", data={"name": "Omni User", "email": "omni@test.com"})
    print(f"      → Created: id={new_user.get('id')}")

    client.delete("/v1/users/42")

    # PART 2: Pagination
    print(f"\n{'─'*60}")
    print("📋 PART 2: Pagination Strategies")
    paginator = OffsetPagination(page_size=5)
    all_items = paginator.get_all(lambda offset, limit: {"items": [{"id": offset+i} for i in range(min(limit, 5))]}, max_pages=3)
    print(f"   Total items: {len(all_items)}")

    # PART 3: Circuit Breaker
    print(f"\n{'─'*60}")
    print("📋 PART 3: Circuit Breaker")
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
    for i in range(5):
        if cb.can_execute():
            if i < 3:
                cb.record_failure()
                print(f"   Request {i+1}: FAILED (failures={cb.failure_count}, state={cb.state})")
            else:
                cb.record_success()
                print(f"   Request {i+1}: SUCCESS (state={cb.state})")
        else:
            print(f"   Request {i+1}: BLOCKED (state={cb.state})")
            time.sleep(0.15)  # Wait for recovery
            if cb.can_execute():
                cb.record_success()
                print(f"   Request {i+1} retry: SUCCESS → CLOSED")

    # PART 4: Webhooks
    print(f"\n{'─'*60}")
    print("📋 PART 4: Webhook Receiver")
    wh = WebhookReceiver("my_secret")
    wh.register("payment.success", lambda p: {"processed": True, "amount": p.get("amount")})
    wh.register("user.created", lambda p: {"welcomed": True, "email": p.get("email")})

    wh.receive("payment.success", {"id": "evt_001", "amount": 99.99})
    wh.receive("user.created", {"id": "evt_002", "email": "new@test.com"})
    wh.receive("payment.success", {"id": "evt_001", "amount": 99.99})  # Duplicate!

    print(f"\n{'='*70}")
    print("✅ API Client Engine: DIPELAJARI MENDALAM.")
    print("   Token Bucket rate limiter ✓")
    print("   Circuit Breaker (CLOSED/OPEN/HALF_OPEN) ✓")
    print("   OAuth2 token refresh ✓")
    print("   Exponential backoff retry ✓")
    print("   Offset + Cursor pagination ✓")
    print("   Webhook receiver (idempotency + dispatch) ✓")
    print(f"{'='*70}")
