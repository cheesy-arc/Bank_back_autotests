from src.main.ui.pages.catalog_page import CatalogPage
from src.main.ui.steps.catalog_steps import CatalogSteps


def test_count_catalog(page):
    steps = CatalogSteps(page)
    steps.login("standard_user", "secret_sauce")
    assert steps.get_product_count() == 6, "Количество товар не соотвутсвует ожиданиям"

def test_sort_by_name(page):
    steps = CatalogSteps(page)
    steps.login("standard_user", "secret_sauce")

    steps.sort_items("az")
    assert steps.get_product_names() == sorted(steps.get_product_names()), "Товары не отсортированы по имени A-Z"

    steps.sort_items("za")
    assert steps.get_product_names() == sorted(steps.get_product_names(), reverse=True), "Товары не отсортированы по имени Z-A"

def test_sort_by_price(page):
    steps = CatalogSteps(page)
    steps.login("standard_user", "secret_sauce")

    steps.sort_items("lohi")
    assert steps.get_product_prices() == sorted(steps.get_product_prices()), "Товары не отсортированы по цене low -> high"

    steps.sort_items("hilo")
    assert steps.get_product_prices() == sorted(steps.get_product_prices(), reverse=True), "Товары не отсортированы по цене high -> low"

def test_add_to_cart(page):
    steps = CatalogSteps(page)
    steps.login("standard_user", "secret_sauce")

    steps.add_to_cart("Sauce Labs Bike Light")
    assert steps.get_cart_count() == 1

def test_add_and_remove_onesie(page):
    steps = CatalogPage(page)
    steps.login("standard_user", "secret_sauce")

    steps.add_to_cart("Sauce Labs Onesie")
    assert steps.get_cart_count() == 1

    steps.remove_from_cart("Sauce Labs Onesie")
    assert steps.get_cart_count() == 0

def test_product_details_onesie(page):
    steps = CatalogPage(page)
    steps.login("standard_user", "secret_sauce")

    name, price, detailed_name, detailed_price = steps.open_product_details("Sauce Labs Onesie")
    assert name == detailed_name, "Название товара не совпадает"
    assert price == detailed_price, "Цена товара не совпадает"

def test_product_details_fleece_jacket(page):
    steps = CatalogPage(page)
    steps.login("standard_user", "secret_sauce")

    name, price, detailed_name, detailed_price = steps.open_product_details("Sauce Labs Fleece Jacket")
    assert name == detailed_name, "Название товара не совпадает"
    assert price == detailed_price, "Цена товара не совпадает"

def test_remove_item_from_catalog(page):
    steps = CatalogPage(page)
    steps.login("standard_user", "secret_sauce")

    steps.remove_from_cart("Test.allTheThings() T-Shirt (Red)")
    assert steps.get_cart_count() == 0

