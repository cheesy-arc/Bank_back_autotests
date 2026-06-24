from src.main.ui.pages.basket_page import BasketPage
from src.main.ui.pages.catalog_page import CatalogPage
from src.main.ui.pages.checkout_page import CheckoutPage
from src.main.ui.steps.basket_steps import BasketSteps
from src.main.ui.steps.catalog_steps import CatalogSteps


def test_add_item_and_check_in_cart(page):
    catalog = CatalogSteps(page)
    basket = BasketSteps(page)
    catalog.login("standard_user", "secret_sauce")

    catalog.add_to_cart("Sauce Labs Backpack")
    basket.open_cart()
    basket.expect_item_in_cart("Sauce Labs Backpack")

def test_add_items_and_check_in_cart(page):
    catalog = CatalogSteps(page)
    basket = BasketSteps(page)

    catalog.login("standard_user", "secret_sauce")
    catalog.add_to_cart("Sauce Labs Fleece Jacket")
    catalog.add_to_cart("Sauce Labs Bolt T-Shirt")

    basket.open_cart()
    basket.expect_item_in_cart("Sauce Labs Fleece Jacket")
    basket.expect_item_in_cart("Sauce Labs Bolt T-Shirt")

def test_remove_item_from_cart(page):
    catalog = CatalogSteps(page)
    basket = BasketSteps(page)

    catalog.login("standard_user", "secret_sauce")
    catalog.add_to_cart("Sauce Labs Fleece Jacket")

    basket.open_cart()
    basket.expect_item_in_cart("Sauce Labs Fleece Jacket")
    basket.remove_item("Sauce Labs Fleece Jacket")
    basket.expect_item_not_in_cart("Sauce Labs Fleece Jacket")

def test_remove_items_from_cart(page):
    catalog = CatalogSteps(page)
    basket = BasketSteps(page)
    catalog.login("standard_user", "secret_sauce")

    catalog.add_to_cart("Sauce Labs Backpack")
    catalog.add_to_cart("Test.allTheThings() T-Shirt (Red)")

    basket.open_cart()
    basket.expect_item_in_cart("Sauce Labs Backpack")
    basket.expect_item_in_cart("Test.allTheThings() T-Shirt (Red)")
    basket.remove_item("Sauce Labs Backpack")
    basket.remove_item("Test.allTheThings() T-Shirt (Red")
    basket.expect_item_not_in_cart("Sauce Labs Backpack")
    basket.expect_item_not_in_cart("Test.allTheThings() T-Shirt (Red")

def test_checkout_multiple_items(page):
    catalog = CatalogSteps(page)
    basket = BasketSteps(page)
    checkout = CheckoutPage(page)
    catalog.login("standard_user", "secret_sauce")

    catalog.add_to_cart("Sauce Labs Bike Light")
    catalog.add_to_cart("Sauce Labs Backpack")
    basket.open_cart()
    basket.expect_item_in_cart("Sauce Labs Bike Light")
    basket.expect_item_in_cart("Sauce Labs Backpack")
    basket_total = basket.get_items_total_price()

    basket.checkout()
    checkout.start_checkout(first_name="Жопа", last_name="Из говна", postal_code="676767")
    checkout_total = checkout.get_item_total_after_continue()
    assert basket_total == checkout_total, "Сумма товаров в коризине и при оформлении заказа не совпадает"

def test_checkout_without_postal_code(page):
    catalog = CatalogSteps(page)
    basket = BasketSteps(page)
    checkout = CheckoutPage(page)
    catalog.login("standard_user", "secret_sauce")

    catalog.add_to_cart("Sauce Labs Fleece Jacket")
    basket.open_cart()
    basket.expect_item_in_cart("Sauce Labs Fleece Jacket")

    basket.checkout()
    checkout.start_checkout(first_name="Говна", last_name="Полон рот", postal_code="")

    error_text = checkout.get_error_text()
    assert error_text != "", "Ожидалась ошибка при оформлении пустой корзины"






