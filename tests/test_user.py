import re

from playwright.sync_api import Page, expect


def test_click_register_button_opens_register_page(auth_page: Page) -> None:
    auth_page.goto("/usuario/listar")
    auth_page.get_by_role("button", name="Cadastrar Usuário").click()

    expect(auth_page).to_have_url("/usuario/cadastrar")


def test_click_edit_button_opens_edit_page(auth_page: Page) -> None:
    auth_page.goto("/usuario/listar")
    auth_page.get_by_role("link", name="Editar").first.click()

    expect(auth_page).to_have_url(re.compile(r"/usuario/editar/\d+"))
