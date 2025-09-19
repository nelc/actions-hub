

def login_user(page, base_url: str, email: str, password: str):
    """
    Logs in a user using the login form.


    Args:
    page: Playwright Page object.
    base_url (str): Base URL of the application.
    email (str): User email.
    password (str): User password.
    """
    page.goto(f"{base_url}/login")
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
