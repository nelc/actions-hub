import argparse

from playwright.sync_api import sync_playwright


def test_plugin_versions(base_url: str, plugins: list[str]) -> None:
    """
    Smoke test to verify that plugin info endpoints return a valid JSON with version info.

    Args:
        base_url (str): The base URL of the LMS.
        plugins (list[str]): List of plugins to check.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        for plugin in plugins:
            full_url = f"{base_url.rstrip('/')}/{plugin}/eox-info"
            print(f"→ Checking {full_url}...")

            response = page.goto(full_url)
            assert response is not None and response.ok, f"❌ Failed to load {full_url}"

            try:
                json_data = response.json()
            except Exception as e:
                raise AssertionError(f"❌ Invalid JSON response from {full_url}: {e}")

            version = json_data.get("version")
            assert version, f"❌ 'version' key not found in JSON from {full_url}"

            print(f"✅ {plugin} version: {version}")

        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke test: Validate eox plugins")
    parser.add_argument("--base-url", required=True, help="Base LMS URL")
    parser.add_argument("--plugins", nargs="+", required=True, help="List of plugin to check")
    args = parser.parse_args()

    test_plugin_versions(base_url=args.base_url, plugins=args.plugins)
