from playwright.sync_api import sync_playwright

import re

def extract_popular_times(page):
    # Scroll to force rendering
    page.mouse.wheel(0, 2000)
    page.wait_for_timeout(1500)

    # Grab all bars with aria-labels
    bars = page.query_selector_all("div[aria-label*='Live']", "div[aria-label*='busy']", "div[aria-label*='gets']", "div[aria-label*='usual']")

    data = {}

    for bar in bars:
        label = bar.get_attribute("aria-label")
        if not label:
            continue

        # Example: "Monday at 6 PM: Usually as busy as it gets"
        match = re.match(r"(\w+) at (\d{1,2}) (AM|PM): (.+)", label)
        if not match:
            continue

        day, hour_str, am_pm, status = match.groups()

        hour = int(hour_str)
        if am_pm == "PM" and hour != 12:
            hour += 12
        elif am_pm == "AM" and hour == 12:
            hour = 0

        if day not in data:
            data[day] = {}

        data[day][hour] = status

    return data

def extract_live_busyness(page):
    # Scroll to force rendering
    page.mouse.wheel(0, 2000)
    page.wait_for_timeout(1500)

    # Find the live bar
    live_el = page.query_selector("div[aria-label^='Live']")

    if not live_el:
        return None  # No live data available

    label = live_el.get_attribute("aria-label")

    # label looks like: "Live: As busy as it gets"
    live_status = label.replace("Live: ", "").strip()

    return live_status


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="user_data",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--flag-switches-begin --disable-site-isolation-trials --flag-switches-end",
            ],
        )

        page = browser.new_page()

        # Patch webdriver
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Patch plugins
        page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1,2,3,4,5]
            });
        """)

        # Patch mimeTypes
        page.add_init_script("""
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => [1,2,3]
            });
        """)

        # UA override
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        })

        url = "https://www.google.com/maps/place/ARC+@+UBC+Life+Building/@49.2674872,-123.2548984,16z/data=!3m2!4b1!5s0x548672b7009e8157:0x8d144bee47b41b26!4m6!3m5!1s0x548672b76ec21be7:0xb8c25e9971701a17!8m2!3d49.2674838!4d-123.2500275!16s%2Fg%2F1tfrrlwn?entry=ttu&g_ep=EgoyMDI2MDExMy4wIKXMDSoASAFQAw%3D%3D"
        print("Loading:", url)

        # Load the URL without waiting for networkidle
        page.goto(url, wait_until="domcontentloaded")

        # Give Maps a moment to settle
        page.wait_for_timeout(1500)
        

        # Extract Popular Times
        # popular_times = extract_popular_times(page)
        live_status = extract_live_busyness(page)

        # print("\nPopular Times Data:")
        # for entry in popular_times:
        #     print(" -", entry)

        print("\nPopular Times Data:")
        if live_status is None:
            print("No live busyness data available")
        else:
            print("Live busyness:", live_status)

        input("\nPress Enter to close...")
        browser.close()

if __name__ == "__main__":
    run()