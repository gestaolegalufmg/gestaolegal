from playwright.sync_api import Page, expect


# TODO(Andre): Check the full form structure
def test_file_register_page_title(auth_page: Page) -> None:
    auth_page.goto("/arquivos/cadastrar_arquivo")

    # TODO(Andre): Understand why get_by_label isn't working as expect
    expect(auth_page.get_by_text("Título *", exact=True)).to_be_visible()
