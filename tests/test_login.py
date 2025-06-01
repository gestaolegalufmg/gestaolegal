from playwright.sync_api import Playwright, expect


def test_login_sucessful(page) -> None:
    page.goto("/usuario/login")
    page.locator("#login").click()
    page.locator("#login").fill("admin@gl.com")
    page.locator("#login").press("Tab")
    page.locator("#senha").fill("123456")
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url("/")


def test_login_empty_password_failure(page) -> None:
    page.goto("/usuario/login")
    page.locator("#login").click()
    page.locator("#login").fill("admin@gl.com")
    page.get_by_role("button", name="Login").click()

    expect(page.locator(".was-validated #senha:invalid")).to_be_visible()

def test_login_wrong_password_failure(page) -> None:
    page.goto("/usuario/login")
    page.locator("#login").click()
    page.locator("#login").fill("admin@gl.com")
    page.locator("#senha").click()
    page.locator("#senha").fill("wrongpasswordcouldneverwork")
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url("/usuario/login")
    page.locator("div").filter(has_text="Atenção:Senha inválida!").nth(2)

def test_login_wrong_password_failure(page) -> None:
    page.goto("/usuario/login")
    page.locator("#login").click()
    page.locator("#login").fill("admin@gl.com")
    page.locator("#senha").click()
    page.locator("#senha").fill("non existing password for testing")
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url("/usuario/login")
    page.locator("div").filter(has_text="Atenção:Senha inválida!").nth(2)

def test_login_wrong_email_failure(page) -> None:
    page.goto("/usuario/login")
    page.locator("#login").click()
    page.locator("#login").fill("admin_non_existing@gl.com")
    page.locator("#senha").click()
    page.locator("#senha").fill("123456")
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url("/usuario/login")
    page.locator("div").filter(has_text="Atenção:Email inválido!").nth(2)

def test_login_invalid_email_failure(page) -> None:
    page.goto("/usuario/login")
    page.locator("#login").click()
    page.locator("#login").fill("username")
    page.locator("#senha").click()
    page.locator("#senha").fill("123456")
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url("/usuario/login")
    expect(page.locator(".was-validated #login:invalid")).to_be_visible()
