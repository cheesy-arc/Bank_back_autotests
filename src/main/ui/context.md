### ./tests/test_catalog.py
from playwright.sync_api import expect


def test_count_catalog(auth_page):
    products = auth_page.locator(".inventory_item")
    assert products.count() == 6

def test_sorted_by_name(auth_page):
    sort_select = auth_page.locator(".product_sort_container")
    expect(sort_select).to_be_visible(timeout=5000)

    sort_select.select_option("az")

    names = auth_page.locator(".inventiry_item_name").all_text_contents()
    assert names == sorted(names), "Товары не отсортированы по имени A-Z"

def test_sorted_by_name_z_to_a(auth_page):
    sort_select = auth_page.locator(".product_sort_container")
    expect(sort_select).to_be_visible(timeout=5000)

    sort_select.select_option("za")

    names = auth_page.locator(".inventory_item_name").all_text_contents()
    assert names == sorted(names, reverse=True), "Товары не отсортированы по имени Z-A"

def test_sort_by_price(auth_page):
    sort_select = auth_page.locator(".product_sort_container")
    expect(sort_select).to_be_visible(timeout=5000)

    sort_select.select_option("lohi")
    prices_text = auth_page.locator(".inventory_item_price").all_text_contents()
    prices = [float(p.replace("$", "")) for p in prices_text]
    assert prices == sorted(prices), "Товары не отсортированы по цене low -> high"

    sort_select.select_option("hilo")
    prices_text = auth_page.locator(".inventory_item_price").all_text_contents()
    prices = [float(p.replace("$", "")) for p in prices_text]
    assert prices == sorted(prices, reverse=True), "Товары не отсортированы по цене high -> low"

def test_add_to_cart(auth_page):
    product_cart = auth_page.locator(".inventory_item", has_text="Sauce Labs Bike Light")
    add_button = product_cart.locator("button")
    add_button.click()

    expect(add_button).to_have_text("Remove")
    expect(auth_page.locator(".shopping_cart_badge")).to_have_text("1")

def test_add_sauce_labs_onesie_to_cart(auth_page):
    product_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Onesie")
    add_button = product_card.locator("button")
    add_button.click()

    expect(add_button).to_have_text("Remove")
    expect(auth_page.locator(".shopping_cart_badge")).to_have_text("1")

    add_button.click()
    expect(add_button).to_have_text("Add to cart")
    expect(auth_page.locator(".shopping_cart_badge")).not_to_be_visible()

def test_product_details_onesie(auth_page):
    product_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Onesie")
    product_name = product_card.locator('[data-test="inventory-item-name"]').inner_text()
    product_price = product_card.locator('[data-test="inventory-item-price"]').inner_text()

    product_card.locator('[data-test="inventory-item-name"]').click()

    detailed_name = auth_page.locator('[data-test="inventory-item-name"]').inner_text()
    detailed_price = auth_page.locator('[data-test="inventory-item-price"]').inner_text()

    assert detailed_name == product_name, "Название товара не совпадают"
    assert detailed_price == product_price, "Цена товара не совпадает"

def test_product_details_fleece_jacket(auth_page):
    product_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Fleece Jacket")
    product_name = product_card.locator('[data-test="inventory-item-name"]').inner_text()
    product_price = product_card.locator('[data-test="inventory-item-price"]').inner_text()

    product_card.locator('[data-test="inventory-item-name"]').click()

    detailed_name = auth_page.locator('[data-test="inventory-item-name"]').inner_text()
    detailed_price = auth_page.locator('[data-test="inventory-item-price"]').inner_text()

    assert detailed_name == product_name, "Название товара не совпадают"
    assert detailed_price == product_price, "Цена товара не совпадает"

def test_remove_item_from_catalog(auth_page):
    product_card = auth_page.locator(".inventory_item", has_text="Test.allTheThings() T-Shirt (Red)")
    product_button = product_card.locator('[data-test="add-to-cart-test.allthethings()-t-shirt-(red)"]')
    product_button.click()

    remove_button = product_card.locator('[data-test="remove-test.allthethings()-t-shirt-(red)"]')
    assert remove_button.is_visible(), "Кнопка Remove не появилась"

    remove_button.click()
    add_button = product_card.locator('[data-test="add-to-cart-test.allthethings()-t-shirt-(red)"]')
    assert add_button.is_visible(), "Кнопка Add to cart не вернулась после удаления"

def test_remove_item_from_catalog_onesie(auth_page):
    product_card = auth_page.locator(".inventory_item", has_text="Sauce Labs Onesie")
    product_button = product_card.locator('[data-test="add-to-cart-sauce-labs-onesie"]')
    product_button.click()

    remove_button = product_card.locator('[data-test="remove-sauce-labs-onesie"]')
    assert remove_button.is_visible(), "Кнопка Remove не появилась"

    remove_button.click()

    add_button = product_card.locator('[data-test="add-to-cart-sauce-labs-onesie"]')
    assert add_button.is_visible(), "Кнопка Add to cart не вернулась после удаления"
### ./tests/test_basket.py
from playwright.sync_api import expect

def test_add_item_and_check_in_cart(auth_page):
    auth_page.locator("#add-to-cart-sauce-labs-backpack").click()
    auth_page.locator(".shopping_cart_link").click()

    item_name = auth_page.locator('[data-test="inventory-item-name"]')
    assert item_name.inner_text() == "Sauce Labs Backpack"

def test_add_items_and_check_in_cart(auth_page):
    auth_page.locator("#add-to-cart-sauce-labs-fleece-jacket").click()
    auth_page.locator("#add-to-cart-sauce-labs-bolt-t-shirt").click()
    auth_page.locator(".shopping_cart_link").click()

    items_names = auth_page.locator('.inventory_item_name').all_text_contents()
    assert items_names == ["Sauce Labs Fleece Jacket", "Sauce Labs Bolt T-Shirt"]

def test_remove_item_from_cart(auth_page):
    auth_page.locator("#add-to-cart-sauce-labs-fleece-jacket").click()
    auth_page.locator(".shopping_cart_link").click()
    jacket = auth_page.locator(".inventory_item_name", has_text='Sauce Labs Fleece Jacket')
    expect(jacket).to_be_visible()

    auth_page.locator("#remove-sauce-labs-fleece-jacket").click()
    expect(jacket).not_to_be_visible()

def test_remove_items_from_cart(auth_page):
    auth_page.locator("#add-to-cart-sauce-labs-backpack").click()
    t_shirt_block = auth_page.locator(".inventory_item", has_text="Test.allTheThings() T-Shirt (Red)")
    t_shirt_block.locator("button").click()
    auth_page.locator(".shopping_cart_link").click()
    backpack = auth_page.locator(".inventory_item_name", has_text='Sauce Labs Backpack')
    t_shirt = auth_page.locator(".inventory_item_name", has_text='Test.allTheThings() T-Shirt (Red)')
    expect(backpack).to_be_visible()
    expect(t_shirt).to_be_visible()

    t_shirt_block = auth_page.locator(".cart_item", has_text="Test.allTheThings() T-Shirt (Red)")
    t_shirt_block.locator("button").click()
    auth_page.locator("#remove-sauce-labs-backpack").click()
    expect(backpack).not_to_be_visible()
    expect(t_shirt).not_to_be_visible()

def test_checkout_multiple_items(auth_page):
    auth_page.locator("#add-to-cart-sauce-labs-bike-light").click()
    auth_page.locator("#add-to-cart-sauce-labs-backpack").click()
    auth_page.locator(".shopping_cart_link").click()
    expect(auth_page.locator(".inventory_item_name", has_text="Sauce Labs Bike Light")).to_be_visible()
    expect(auth_page.locator(".inventory_item_name", has_text="Sauce Labs Backpack")).to_be_visible()

    prices_text = auth_page.locator(".inventory_item_price").all_text_contents()
    prices = [float(p.replace("$", "")) for p in prices_text]
    expected_total = sum(prices)

    auth_page.locator("#checkout").click()
    auth_page.locator("#first-name").fill("Жопа")
    auth_page.locator("#last-name").fill("Из говна")
    auth_page.locator("#postal-code").fill("676767")
    auth_page.locator("#continue").click()

    items_total_text = auth_page.locator(".summary_subtotal_label").inner_text()
    items_total = float(items_total_text.split("$")[1])
    assert items_total == expected_total, "Сумма заказа не совпадает на странцие оформления заказа"

    tax_text = auth_page.locator(".summary_tax_label").inner_text()
    tax = float(tax_text.split("$")[1])
    total_text = auth_page.locator(".summary_total_label").inner_text()
    total_price = float(total_text.split("$")[1])

    assert tax + expected_total == total_price, "Сумма всего заказа не совпадает с суммой заказа + налог"

    auth_page.locator("#finish").click()
    success_message = auth_page.locator(".complete-header")
    expect(success_message).to_have_text("Thank you for your order!")

def test_checkout_without_items(page):
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.locator("#login-button").click()

    page.locator("#add-to-cart-sauce-labs-fleece-jacket").click()
    page.locator(".shopping_cart_link").click()
    expect(page.locator(".inventory_item_name", has_text="Sauce Labs Fleece Jacket")).to_be_visible()

    page.locator("#checkout").click()

    page.locator("#first-name").fill("Жопа")
    page.locator("#last-name").fill("Из говна")
    page.locator("#continue").click()

    error_message = page.locator('[data-test="error"]')
    expect(error_message).to_have_text("Error: Postal Code is required")





### ./tests/test_auth.py
from playwright.sync_api import expect

from src.main.ui.pages.login_page import LoginPage


def test_auth(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")

def test_login_locked_out_user(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("locked_out_user", "secret_sauce")

    expect(page).to_have_url('https://www.saucedemo.com/')
    error_text = login_page.error_message
    assert "locked out" in error_text

def test_logout(auth_page):
    page = auth_page
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")

    page.locator('#react-burger-menu-btn').click()
    page.locator('#logout_sidebar_link').click()

    expect(page).to_have_url('https://www.saucedemo.com/')
    expect(page.locator('#login-button')).to_be_visible()

def test_logout_visual_user(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("visual_user", "secret_sauce")
    expect(page).to_have_url('https://www.saucedemo.com/inventory.html')

    page.locator("#react-burger-menu-btn").click()
    page.locator("#logout_sidebar_link").click()

    expect(page).to_have_url("https://www.saucedemo.com/")
    expect(page.locator("#login-button")).to_be_visible()




### ./fixtures/ui_fixtures.py
import pytest
from playwright.sync_api import sync_playwright
from sqlalchemy.util import parse_user_argument_for_enum


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright

@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=False)
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

@pytest.fixture(scope="function")
def auth_page(page):
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.locator("#login-button").click()
    return page
### ./pages/login_page.py
from playwright.sync_api import Page, expect

class LoginPage:
    URL = "https://www.saucedemo.com/"

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.get_by_placeholder("Username")
        self.password_input = page.get_by_placeholder("Password")
        self.login_button = page.locator("#login-button")
        self.error_message = page.locator("[data-test='error']").inner_text()

    def open(self):
        self.page.goto(self.URL)

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def get_error_text(self) -> str:
        return self.error_message.inner_text()