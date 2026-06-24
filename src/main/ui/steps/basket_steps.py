import allure
from playwright.sync_api import Page, expect
from src.main.ui.pages.basket_page import BasketPage


class BasketSteps:
    def __init__(self, page: Page):
        self.page = page
        self.basket = BasketPage(page)

    @allure.step("Открываем корзину")
    def open_cart(self):
        self.basket.open_cart()
        return self

    @allure.step("Проверяем, что товар {product_name} находится в корзине")
    def expect_item_in_cart(self, product_name: str):
        self.basket.expect_item_in_cart(product_name)
        return self

    @allure.step("Проверяем, что товар {product_name} не в корзине")
    def expect_item_not_in_cart(self, product_name: str):
        self.basket.expect_item_not_in_cart(product_name)
        return self

    @allure.step("Удаляем товар из корзны, товар из корзины {product_name}")
    def remove_item(self, product_name: str):
        self.basket.remove_item(product_name)
        return self

    @allure.step("Переходим к Checkout")
    def checkout(self):
        self.basket.checkout()
        return self

    @allure.step("Получаем список названий товаров в корзине")
    def get_items_names(self) -> list[str]:
        return self.basket.get_item_names()

    @allure.step("Получаем общую сумму товаров в корзине")
    def get_items_total_price(self) -> float:
        return self.basket.get_items_total_price()

class CheckoutSteps:
    def __init__(self, page: Page):
        self.page = page
        self.checkout = CheckoutSteps(page)

    @allure.step("Начинаем Checkout: {first_name}, {last_name}, {postal_code}")
    def start_checkout(self, first_name: str, last_name: str, postal_code: str):
        self.checkout.start_checkout(first_name, last_name, postal_code)
        return self

    @allure.step("Завершаем Checkout")
    def finish_checkout(self):
        self.checkout.finish_checkout()
        return self

    @allure.step("Получаем текст ошибки на Checkout")
    def get_error_text(self) -> str:
        return self.checkout.get_error_text()

    @allure.step("Получаем сумму товаров после Continue")
    def get_item_total_after_continue(self) -> float:
        return self.checkout.get_item_total_after_continue()
