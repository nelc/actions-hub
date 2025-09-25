import argparse

from playwright.sync_api import TimeoutError, sync_playwright
from utils import login_user


def test_complete_multiplechoice_unit(base_url: str, course_id: str, unit_id: str, email: str, password: str):
    """
    Smoke test to verify that a multiple choice unit can be completed.

    Args:
        base_url (str): The base URL of the platform.
        course_id (str): The course ID to navigate into.
        unit_id (str): The specific unit ID (usage key).
        email (str): Login email.
        password (str): Login password.
    """
    unit_url = f"{base_url}/courses/{course_id}/jump_to_id/{unit_id}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        login_user(page, base_url, email, password)
        page.goto(unit_url)
        page.wait_for_load_state("networkidle")

        # Try to find the iframe that contains the unit content
        iframe = page.frame_locator("#unit-iframe")
        assert iframe is not None, "No iframe found containing unit content"

        # Get the first problem
        problems = iframe.locator("div.problem")
        assert problems.count() > 0, "No problems found"
        problem = problems.first

        # Get problem choices
        radios = problem.locator("input[type='radio']")
        assert radios.count() > 0, "No multiple choice options found"

        # Get Submit button
        submit_button = problem.locator("button.submit")
        assert submit_button.is_visible(), "Submit button not found"

        for radio in radios.all():
            radio.click()
            submit_button.click()
            notification = problem.locator(".notification.success.notification-submit")

            try:
                notification.wait_for(state="visible", timeout=5000)
                break
            except TimeoutError:
                continue

        assert notification.is_visible(), "Success notification isn't visible"

        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke test: Complete a multiple choice unit")
    parser.add_argument("--base-url", required=True, help="Base URL of the LMS")
    parser.add_argument("--course-id", required=True, help="Course ID")
    parser.add_argument("--unit-id", required=True, help="Unit ID (usage key)")
    parser.add_argument("--email", required=True, help="User email for login")
    parser.add_argument("--password", required=True, help="User password for login")
    args = parser.parse_args()

    test_complete_multiplechoice_unit(
        base_url=args.base_url,
        course_id=args.course_id,
        unit_id=args.unit_id,
        email=args.email,
        password=args.password,
    )
