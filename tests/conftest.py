import os

import pytest


@pytest.fixture(scope="session")
def browser_context_with_auth(browser, base_url: str):
    context = browser.new_context(base_url=base_url)
    page = context.new_page()

    page.goto("/usuario/login")
    page.locator("#login").fill("admin@gl.com")
    page.locator("#senha").fill("123456")
    page.get_by_role("button", name="Login").click()

    page.wait_for_url("/")

    auth_file = "./auth_state.json"
    context.storage_state(path=auth_file)

    context.close()
    yield context

    if os.path.exists(auth_file):
        os.remove(auth_file)


@pytest.fixture
def auth_page(browser, browser_context_with_auth, base_url: str):
    context = browser.new_context(storage_state="./auth_state.json", base_url=base_url)
    page = context.new_page()
    yield page
    context.close()
