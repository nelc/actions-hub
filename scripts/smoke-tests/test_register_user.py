import argparse
import random
import string

from playwright.sync_api import expect, sync_playwright


def random_string(length=6):
    """
    Generate a random alphanumeric string of the given length.

    Args:
        length (int): Length of the string to generate. Default is 6.

    Returns:
        str: Random string composed of lowercase letters and digits.
    """
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def fill_required_fields(page):
    """
    Fills all required input and select fields within the registration form.

    It handles different input types (text, email, password) and selects the
    first valid option for dropdown fields.

    Args:
        page: A Playwright Page instance already loaded with the registration form.
    """
    required_fields = page.locator(".required-fields > div")

    for field_index in range(required_fields.count()):
        field = required_fields.nth(field_index)

        # Check if it's an input
        if field.locator("input").count() > 0:
            input_field = field.locator("input").first
            input_name = input_field.get_attribute("name")
            input_type = input_field.get_attribute("type") or ""

            if input_type == "email":
                input_field.fill(f"testuser_{random_string()}@example.com")
            elif input_type == "text" and input_name == "arabic_name":
                input_field.fill("مستخدم اختبار")
            elif input_type == "text" and input_name == "national_id":
                input_field.fill(str(random.randint(4000000000, 9999999999)))
            elif input_type == "text":
                input_field.fill(f"Test{random_string()}")
            elif input_type == "password":
                input_field.fill("StrongPass123!")
            elif input_type == "hidden":
                continue
            else:
                input_field.fill("placeholder")

        # Check if it's a select dropdown
        elif field.locator("select").count() > 0:
            select_field = field.locator("select").first
            options = select_field.locator("option")

            for option_index in range(options.count()):
                value = options.nth(option_index).get_attribute("value")
                if value and value != "":
                    select_field.select_option(value=value)
                    break


def test_register_user(base_url: str):
    """
    Smoke test to register a new user on the Open edX platform.

    Navigates to the registration page, fills all required fields,
    submits the form, and checks whether the registration was successful.

    Args:
        base_url (str): The base URL of the LMS.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{base_url}/register")

        # Fill required fields
        fill_required_fields(page)

        # Submit form
        page.locator("#register-form button[type='submit']").click()

        # Wait for redirection or error
        page.wait_for_load_state("networkidle")
        error_box = page.locator("div.js-form-errors.status.submission-error")

        if error_box.is_visible():
            error_text = error_box.locator("ul.message-copy").inner_text()
            raise AssertionError(f"❌ Registration failed: {error_text}")

        expect(page).to_have_url(f"{base_url}/dashboard")

        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke test: User registration")
    parser.add_argument("--base-url", required=True, help="Base LMS URL")
    args = parser.parse_args()

    test_register_user(base_url=args.base_url)
