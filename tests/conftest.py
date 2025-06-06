import pytest


@pytest.fixture(scope="session")
def browser_context_with_auth(browser, base_url: str):
    context = browser.new_context(base_url=base_url)
    page = context.new_page()

    page.goto("/usuario/login")
    page.locator("#login").click()
    page.locator("#login").fill("admin@gl.com")
    page.locator("#login").press("Tab")
    page.locator("#senha").fill("123456")
    page.get_by_role("button", name="Login").click()

    context.storage_state(path="./auth_state.json")

    yield context
    context.close()


@pytest.fixture
def auth_page(browser, base_url: str):
    context = browser.new_context(storage_state="./auth_state.json", base_url=base_url)
    page = context.new_page()

    yield page

    context.close()
