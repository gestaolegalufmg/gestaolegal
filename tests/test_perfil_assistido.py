import re

from playwright.sync_api import Page, expect


# INFO: We are currently only filling the required fields
# TODO(Andre): Test with other fields configurations
def register_atendido(page: Page):
    page.goto("/plantao/novo_atendimento")

    page.get_by_role("textbox", name="Nome *").click()
    page.get_by_role("textbox", name="Nome *").fill("Atendido Teste 1")
    page.get_by_role("textbox", name="Data de nascimento *").fill("2000-02-02")
    page.locator("#formcpf").click()
    page.locator("#formcpf").fill("999.999.999-99")
    page.get_by_text("Nome * Data de nascimento *").click()
    page.locator("#formcel").click()
    page.locator("#formcel").fill("(99) 99999-9999")
    page.locator("#formcep").click()
    page.locator("#formcep").fill("64000-210")
    page.get_by_role("textbox", name="Número *").click()

    page.wait_for_timeout(1000)
    page.get_by_role("textbox", name="Número *").fill("12")
    page.wait_for_timeout(1000)

    page.get_by_role("button", name="Cadastrar", exact=True).click()


def test_register_atendido_required_fields(auth_page: Page):
    register_atendido(auth_page)
    expect(auth_page).to_have_url(re.compile(r"/atendido/perfil_assistido/\d+"))


# TODO(Andre): Also check the inner card fields, not just the title
def test_view_atendido_profile(auth_page: Page):
    register_atendido(auth_page)
    auth_page.goto("/atendido/perfil_assistido/1")

    expect(auth_page.get_by_text("Dados de Atendimento")).to_be_visible()
    expect(auth_page.get_by_text("Endereço")).to_be_visible()
    expect(
        auth_page.get_by_role("heading", name="Orientações Jurídicas")
    ).to_be_visible()


def test_assistido_info_should_not_be_visible_on_atendido_page(auth_page: Page):
    register_atendido(auth_page)
    auth_page.goto("/atendido/perfil_assistido/1")
    expect(auth_page.get_by_text("Dados de Assistido")).to_be_hidden()
    expect(auth_page.get_by_text("Renda e Patrimônio")).to_be_hidden()
    expect(auth_page.get_by_text("Casos Vinculados")).to_be_hidden()
