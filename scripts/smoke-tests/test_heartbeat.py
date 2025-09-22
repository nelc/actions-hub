import argparse

from playwright.sync_api import sync_playwright


def test_heartbeat(base_url: str):
    """
    Smoke test to verify that the /heartbeat endpoint is reachable and returns HTTP 200.

    Args:
        base_url (str): The base URL of the platform.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        response = page.goto(f"{base_url.rstrip('/')}/heartbeat")

        if not response or response.status != 200:
            raise AssertionError(
                f"❌ Heartbeat check failed. Status: {response.status if response else 'No response'}"
            )

        print(f"✅ Heartbeat responded with HTTP {response.status}")

        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke test: Heartbeat Endpoint")
    parser.add_argument("--base-url", required=True, help="Base URL of the platform")
    args = parser.parse_args()

    test_heartbeat(base_url=args.base_url)
