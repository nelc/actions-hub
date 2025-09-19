import argparse

from playwright.sync_api import expect, sync_playwright
from utils import login_user


def test_view_course(base_url: str, course_id: str, email: str, password: str):
    """
    Smoke test to verify that a course page is accessible and loads key content.

    Args:
        base_url (str): The base URL of the platform.
        course_id (str): The course identifier.
        email (str): The user email to log in.
        password (str): The user password to log in.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        login_user(page, base_url, email, password)

        course_url = f"{base_url}/learning/course/{course_id}/home"
        page.wait_for_load_state("networkidle")
        page.goto(course_url)

        expect(page).to_have_url(course_url)
        expect(page.locator("ol#courseHome-outline li").first).to_be_visible()
        assert page.locator("ol#courseHome-outline li").count() > 0
        assert page.locator("div#courseTabsNavigation .container-xl nav a").count() > 1

        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke test: View Course Page")
    parser.add_argument("--base-url", required=True, help="Base URL of the platform")
    parser.add_argument("--course-id", required=True, help="Course ID to visit")
    parser.add_argument("--email", required=True, help="User email for login")
    parser.add_argument("--password", required=True, help="User password for login")
    args = parser.parse_args()

    test_view_course(
        base_url=args.base_url,
        course_id=args.course_id,
        email=args.email,
        password=args.password,
    )
