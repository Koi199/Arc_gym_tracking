from playwright.sync_api import sync_playwright

URL = "https://www.google.com/maps/place/ARC+@+UBC+Life+Building/@49.2674838,-123.2526024,17z/data=!3m1!4b1!4m6!3m5!1s0x548672b76ec21be7:0xb8c25e9971701a17!8m2!3d49.2674838!4d-123.2500275!16s%2Fg%2F1tfrrlwn?entry=ttu&g_ep=EgoyMDI2MDExMy4wIKXMDSoASAFQAw%3D%3D"

def scrape_live_busyness():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ))

        # Remove webdriver flag
        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        page.goto(URL, timeout=60000)

        # Wait for dynamic content
        page.wait_for_timeout(5000)

        # Try multiple selectors
        selectors = [
            'div[aria-label*="Live"]',
            'div[aria-label*="busy"]',
            'div[aria-label*="%"]'
        ]

        for sel in selectors:
            try:
                el = page.query_selector(sel)
                if el:
                    print("Found:", el.get_attribute("aria-label"))
                    return el.get_attribute("aria-label")
            except:
                pass

        print("No live busyness found.")
        return None

if __name__ == "__main__":
    scrape_live_busyness()
