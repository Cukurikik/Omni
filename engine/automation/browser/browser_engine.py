import time
import random
import hashlib

# ==========================================
# 🎭 OMNI AUTOMATION: Browser Automation Engine (Phase 159)
# ==========================================
#
# PROSES BELAJAR:
# ──────────────────────
# Browser automation ≠ HTTP scraping.
# Perbedaan FUNDAMENTAL:
# - HTTP scraping: kirim request, terima HTML statis.
# - Browser automation: kontrol browser NYATA (Chromium, Firefox),
#   JavaScript dieksekusi, DOM di-render, bisa screenshot/PDF.
#
# ARSITEKTUR PLAYWRIGHT:
# 1. Client-Server via PERSISTENT WebSocket (bukan REST per-command)
# 2. Chrome DevTools Protocol (CDP) untuk kontrol rendah
# 3. Browser Context = "incognito profile" (isolated cookies, storage)
# 4. Page Object Model (POM) = pattern untuk maintainable tests
# 5. Locator Strategy: getByRole > getByText > CSS > XPath
#
# vs SELENIUM:
# - Selenium: HTTP REST per command → lambat (chatty protocol)
# - Playwright: WebSocket persistent → event streaming cepat
# - Playwright: auto-wait (built-in), Selenium manual wait

# ─────────────────────────────────────────────────
# KOMPONEN 1: CDP (Chrome DevTools Protocol) Simulator
# ─────────────────────────────────────────────────
class CDPSession:
    """
    PELAJARAN: CDP = low-level API browser.
    Playwright menggunakan CDP untuk kontrol Chromium.
    Untuk Firefox/WebKit, Playwright PATCH browser supaya CDP-compatible.
    """
    def __init__(self, target_id):
        self.target_id = target_id
        self.domain_enabled = set()

    def send(self, method, params=None):
        domain = method.split(".")[0]
        if domain not in self.domain_enabled:
            self.domain_enabled.add(domain)
        result = {"id": random.randint(1, 9999), "method": method}
        print(f"         📡 [CDP] {method}({params or {}})")
        return result

    def enable_domain(self, domain):
        self.send(f"{domain}.enable")


# ─────────────────────────────────────────────────
# KOMPONEN 2: Browser, Context, Page
# ─────────────────────────────────────────────────
class BrowserType:
    """Playwright browser type launcher."""
    def __init__(self, name="chromium"):
        self.name = name

    def launch(self, headless=True):
        print(f"   🚀 [LAUNCH] {self.name} (headless={headless})")
        return Browser(self.name, headless)


class Browser:
    def __init__(self, name, headless):
        self.name = name
        self.headless = headless
        self.contexts = []
        self.cdp = CDPSession(f"browser-{id(self)}")

    def new_context(self, viewport=None, user_agent=None, locale=None):
        """
        PELAJARAN: Browser Context = incognito profile.
        Setiap context punya cookies, storage, dan cache SENDIRI.
        Berguna untuk: multi-user testing, locale testing, dll.
        """
        ctx = BrowserContext(self, viewport, user_agent, locale)
        self.contexts.append(ctx)
        return ctx

    def close(self):
        for ctx in self.contexts:
            ctx.close()
        print(f"   🔒 Browser closed")


class BrowserContext:
    def __init__(self, browser, viewport=None, user_agent=None, locale=None):
        self.browser = browser
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.user_agent = user_agent or "Mozilla/5.0 Playwright"
        self.locale = locale or "en-US"
        self.pages = []
        self.cookies = {}
        self.storage = {}
        print(f"      📋 Context: {self.viewport['width']}x{self.viewport['height']}, locale={self.locale}")

    def new_page(self):
        page = Page(self)
        self.pages.append(page)
        return page

    def add_cookies(self, cookies):
        for c in cookies:
            self.cookies[c["name"]] = c["value"]

    def close(self):
        for page in self.pages:
            page.close()


class Locator:
    """
    PELAJARAN: Playwright Locator = lazy, auto-waiting reference ke element.
    Locator TIDAK langsung cari elemen. Baru saat .click()/.fill()
    dipanggil, Playwright: wait → find → assert visible → act.
    """
    def __init__(self, page, selector, strategy="css"):
        self.page = page
        self.selector = selector
        self.strategy = strategy

    def click(self):
        print(f"         🖱️ Click: [{self.strategy}] {self.selector}")
        self.page.actions.append({"type": "click", "selector": self.selector})
        return self

    def fill(self, value):
        print(f"         ⌨️ Fill: [{self.strategy}] {self.selector} = '{value}'")
        self.page.actions.append({"type": "fill", "selector": self.selector, "value": value})
        return self

    def text_content(self):
        text = f"Content of {self.selector}"
        print(f"         📖 Text: [{self.strategy}] {self.selector} → '{text[:30]}'")
        return text

    def is_visible(self):
        return True

    def count(self):
        return random.randint(1, 5)


class Page:
    """
    PELAJARAN: Page = satu tab browser.
    Semua interaksi (click, type, navigate) terjadi di Page.
    Playwright AUTO-WAIT: sebelum click, tunggu elemen visible + enabled.
    """
    def __init__(self, context):
        self.context = context
        self.url = "about:blank"
        self.title_text = ""
        self.actions = []
        self.screenshots = []
        self.console_logs = []
        self.network_requests = []

    def goto(self, url, wait_until="domcontentloaded"):
        self.url = url
        self.title_text = f"Page: {url}"
        self.actions.append({"type": "navigate", "url": url})
        print(f"      🌐 Navigate: {url} (wait: {wait_until})")
        return self

    def title(self):
        return self.title_text

    # ── Locator Strategies (priority order) ──
    def get_by_role(self, role, name=None):
        """BEST: accessible role-based locator."""
        selector = f"role={role}" + (f"[name='{name}']" if name else "")
        return Locator(self, selector, "role")

    def get_by_text(self, text, exact=False):
        """Good: text content locator."""
        return Locator(self, f"text='{text}'", "text")

    def get_by_label(self, label):
        """Good: form label locator."""
        return Locator(self, f"label='{label}'", "label")

    def get_by_placeholder(self, placeholder):
        return Locator(self, f"placeholder='{placeholder}'", "placeholder")

    def locator(self, selector):
        """Fallback: CSS selector."""
        return Locator(self, selector, "css")

    def query_selector(self, selector):
        """LOW LEVEL: direct CSS query."""
        return Locator(self, selector, "css-direct")

    # ── Actions ──
    def screenshot(self, path="screenshot.png", full_page=False):
        self.screenshots.append(path)
        print(f"      📸 Screenshot: {path} (full_page={full_page})")
        return path

    def wait_for_selector(self, selector, timeout=5000):
        print(f"      ⏳ Wait: {selector} (timeout={timeout}ms)")
        return Locator(self, selector)

    def evaluate(self, expression):
        """Jalankan JavaScript di browser context."""
        print(f"      🔧 JS: {expression[:40]}...")
        return f"result_of_{expression[:10]}"

    def close(self):
        pass


# ─────────────────────────────────────────────────
# KOMPONEN 3: Page Object Model (POM)
# ─────────────────────────────────────────────────
class LoginPage:
    """
    PELAJARAN: POM = encapsulasi UI elements dan interaksi.
    Jika UI berubah, update POM saja — test tetap sama.
    Rules:
    - POM: action methods (login, navigate)
    - Test: assertions + flow
    - JANGAN taruh assertion di POM!
    """
    def __init__(self, page):
        self.page = page
        # Locators (lazy — baru resolve saat dipakai)
        self.email_input = page.get_by_label("Email")
        self.password_input = page.get_by_label("Password")
        self.submit_button = page.get_by_role("button", name="Login")
        self.error_message = page.locator(".error-message")

    def navigate(self):
        self.page.goto("https://app.example.com/login")
        return self

    def login(self, email, password):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
        return DashboardPage(self.page)


class DashboardPage:
    def __init__(self, page):
        self.page = page
        self.welcome_text = page.get_by_role("heading", name="Welcome")
        self.nav_items = page.locator("nav a")

    def get_welcome_message(self):
        return self.welcome_text.text_content()


# ─────────────────────────────────────────────────
# KOMPONEN 4: Network Interception
# ─────────────────────────────────────────────────
class NetworkInterceptor:
    """
    PELAJARAN: Playwright bisa intercept, mock, dan block network requests.
    Berguna untuk testing (mock API), scraping (block images), dan security.
    """
    def __init__(self):
        self.rules = []
        self.intercepted = []

    def route(self, pattern, handler):
        self.rules.append({"pattern": pattern, "handler": handler})
        print(f"      🛡️ Route: {pattern} → {handler.__name__}")

    def intercept(self, url):
        for rule in self.rules:
            if rule["pattern"] in url:
                result = rule["handler"](url)
                self.intercepted.append({"url": url, "result": result})
                return result
        return None


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🎭 OMNI BROWSER — Playwright-Style Automation Engine")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Playwright vs Selenium:")
    print("   - Playwright: WebSocket persistent → cepat, auto-wait")
    print("   - Selenium: HTTP REST per command → lambat, manual wait")
    print("   CDP (Chrome DevTools Protocol) = low-level browser control")
    print("   Browser Context = incognito profile (isolated)")
    print("   Locator = lazy reference, auto-wait sebelum action")
    print("   POM = encapsulasi selectors, update 1 tempat saja")

    # PART 1: Browser launch + context
    print(f"\n{'─'*60}")
    print("📋 PART 1: Browser Launch + Context Isolation")
    chromium = BrowserType("chromium")
    browser = chromium.launch(headless=True)

    # 2 contexts terpisah (cookies/storage TERPISAH)
    ctx1 = browser.new_context(viewport={"width": 1920, "height": 1080}, locale="id-ID")
    ctx2 = browser.new_context(viewport={"width": 375, "height": 667}, locale="en-US")
    print(f"   ✅ 2 isolated contexts (desktop ID + mobile US)")

    # PART 2: Page interactions + Locator strategies
    print(f"\n{'─'*60}")
    print("📋 PART 2: Locator Strategy Hierarchy")
    page = ctx1.new_page()
    page.goto("https://example.com/dashboard")

    print(f"\n   Locator Priority (best → worst):")
    page.get_by_role("button", name="Submit").click()     # 1. BEST: accessible
    page.get_by_text("Click here").click()                 # 2. Good: text
    page.get_by_label("Email").fill("user@omni.dev")       # 3. Good: label
    page.get_by_placeholder("Search...").fill("query")     # 4. OK: placeholder
    page.locator("#submit-btn").click()                     # 5. Fragile: CSS
    page.query_selector("div > span.text").text_content()   # 6. WORST: complex CSS

    # PART 3: Page Object Model
    print(f"\n{'─'*60}")
    print("📋 PART 3: Page Object Model (POM) Pattern")
    page2 = ctx1.new_page()
    login = LoginPage(page2)
    login.navigate()
    dashboard = login.login("admin@omni.dev", "secret123")
    welcome = dashboard.get_welcome_message()
    print(f"   ✅ POM: LoginPage → DashboardPage flow complete")

    # PART 4: Network Interception
    print(f"\n{'─'*60}")
    print("📋 PART 4: Network Interception")
    interceptor = NetworkInterceptor()
    interceptor.route("*.png", lambda url: "BLOCKED_IMAGE")
    interceptor.route("api.analytics.com", lambda url: "BLOCKED_TRACKER")
    interceptor.route("api.backend.com", lambda url: {"data": "mocked_response"})

    interceptor.intercept("https://cdn.example.com/hero.png")
    interceptor.intercept("https://api.analytics.com/track?event=page_view")
    interceptor.intercept("https://api.backend.com/users")
    print(f"   Intercepted: {len(interceptor.intercepted)} requests")

    # PART 5: CDP Session
    print(f"\n{'─'*60}")
    print("📋 PART 5: Chrome DevTools Protocol (CDP)")
    cdp = browser.cdp
    cdp.enable_domain("Network")
    cdp.enable_domain("Performance")
    cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 100})
    cdp.send("Performance.getMetrics")

    page.screenshot("dashboard.png", full_page=True)

    browser.close()

    print(f"\n{'='*70}")
    print("✅ Browser Automation: DIPELAJARI MENDALAM.")
    print("   Playwright architecture (WebSocket + CDP) ✓")
    print("   Browser Context isolation ✓")
    print("   Locator hierarchy (role > text > CSS > XPath) ✓")
    print("   Page Object Model (POM) ✓")
    print("   Network interception (mock/block) ✓")
    print("   CDP direct access ✓ | Auto-wait ✓")
    print(f"{'='*70}")
