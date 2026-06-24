from src.main.ui.pages.catalog_page import CatalogPage
from src.main.ui.steps.catalog_steps import CatalogSteps
from src.main.ui.steps.login_steps import LoginSteps


def test_auth(page):
    login = LoginSteps(page)
    login.open_login_page().login("standard_user", "secret_sauce")
    assert page.url == CatalogSteps.CATALOG_URL, "Ожидаем товары на странице каталога"

def test_login_locked_out_user(page):
    steps = LoginSteps(page)
    steps.open_login_page().login("locked_out_user", "secret_sauce")

    error_text = steps.login_page.get_error_text()
    assert "locked out" in error_text

def test_logout(page):
    login = LoginSteps(page)
    catalog = CatalogSteps(page)

    login.open_login_page().login("standard_user", "secret_sauce")
    assert catalog.get_product_count() > 0, "Ожидается наличие товаров в каталоге"

    catalog.logout()
    assert page.url == login.LOGIN_URL, "Ожидаем возврат на страницу логина"

def test_logout_visual_user(page):
    login = LoginSteps(page)
    catalog = CatalogSteps(page)

    login.open_login_page().login("visual_user", "secret_sauce")
    assert catalog.get_product_count() > 0

    catalog.logout()
    assert page.url == login.LOGIN_URL, "Ожидаем возврат на страницу логина"




