import logging
from playwright.sync_api import Browser
from playwright.sync_api import Request, Route, ConsoleMessage, Dialog
from .test_cases import TestCases
from .demo_pages import DemoPages


class App:
    def __init__(self, browser: Browser, base_url: str, **kwargs):
        self.browser = browser
        self.context = self.browser.new_context(**kwargs)
        self.page = self.context.new_page()
        self.base_url = base_url
        self.test_cases = TestCases(self.page)
        self.demo_pages = DemoPages(self.page)

        def console_handler(message: ConsoleMessage):
            if message.type == 'error':
                logging.error(f'page: {self.page.url}, console_error: {message.text}')

        def dialog_handler(dialog: Dialog):
            logging.warning(f'page: {self.page.url}, dialog text: {dialog.message}')
            dialog.accept()

        self.page.on('console', console_handler)
        self.page.on('dialog', dialog_handler)

    def goto(self, endpoint: str, use_base_url=True):
        if use_base_url:
            self.page.goto(self.base_url + endpoint)
        else:
            self.page.goto(endpoint)

    def navigate_to(self, menu: str):
        self.page.get_by_role("link", name=menu).click()
        self.page.wait_for_load_state()

    def login(self, login: str, password: str):
        self.page.get_by_label("Username:").fill(login)
        self.page.get_by_label("Password:").fill(password)
        self.page.get_by_role("button", name="Login").click()

    def create_test(self, test_name: str, test_description: str):
        self.page.locator("#id_name").fill(test_name)
        self.page.get_by_label("Test description").fill(test_description)
        self.page.get_by_role("button", name="Create").click()

    def check_test_exists(self, test_name='hello'):
        return self.page.get_by_role("row", name=test_name).locator("div") is not None

    def delete_test_by_name(self, test_name: str):
        self.page.get_by_text(test_name)
        self.page.get_by_role("row", name=test_name).get_by_role("button").nth(3).click()

    def click_menu_button(self):
        self.page.click('.menuBtn')

    def is_menu_button_visible(self):
        return self.page.is_visible('.menuBtn')

    def get_location(self):
        return self.page.text_content('.position')

    def intercept_requests(self, url: str, payload: str):
        def handler(route: Route, request: Request):
            route.fulfill(status=200, body=payload)

        self.page.route(url, handler)

    def stop_intercept(self, url: str):
        self.page.unroute(url)

    def refresh_dashboard(self):
        self.page.click('input')

    def get_total_tests_stats(self):
        return self.page.text_content('.total >> span')

    def close(self):
        self.page.close()
        self.context.close()
