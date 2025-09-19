import argparse

from playwright.sync_api import expect, sync_playwright
from utils import login_user


def test_login_user(base_url: str, email: str, password: str) -> None:
    """
    Runs a login smoke test using Playwright against the specified base URL.

    Args:
        base_url (str): Base URL of the target application.
        email (str): Email of the test user.
        password (str): Password of the test user.

    Raises:
        AssertionError: If the login fails or the dashboard page is not reached.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        login_user(page, base_url, email, password)

        expect(page).to_have_url(f"{base_url}/dashboard")

        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run login smoke test using Playwright.")
    parser.add_argument("--base-url", required=True, help="Base URL of the target application.")
    parser.add_argument("--email", required=True, help="Login email.")
    parser.add_argument("--password", required=True, help="Login password.")
    args = parser.parse_args()

    test_login_user(base_url=args.base_url, email=args.email, password=args.password)
