import os
import json
import pytest
import os.path
import logging
from settings import *

from pytest import fixture
from playwright.sync_api import Playwright, sync_playwright, expect
from page_objects.application import App


@fixture(autouse=True, scope='session')
def preconditions():
    logging.info('precondition started')
    yield
    logging.info('postcondition started')


@fixture(scope='session')
def get_playwright():
    with sync_playwright() as playwright:
       yield playwright


@fixture(scope='session', params=['chromium'])
def get_browser(get_playwright, request):
    browser = request.param
    os.environ['PWBROWSER'] = browser
    headless = request.config.getini('headless')
    if headless == 'True':
        headless = True
    else:
        headless = False

    if browser == 'chromium':
        bro = get_playwright.chromium.launch(headless=headless)
    elif browser == 'firefox':
        bro = get_playwright.firefox.launch(headless=headless)
    elif browser == 'webkit':
        bro = get_playwright.webkit.launch(headless=headless)
    else:
        assert False, 'unsupported browser type'
    yield bro
    bro.close()
    del os.environ['PWBROWSER']


@fixture(scope='session')
def desktop_app(get_browser, request):
    base_url = request.config.getini('base_url')
    app = App(get_browser, base_url=base_url)
    app.goto('/')
    yield app
    app.close()


@fixture(scope='session')
def desktop_app_auth(desktop_app, request):
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    desktop_app.goto('/login')
    desktop_app.login(**config)
    yield desktop_app


@fixture(scope='session', params=['iPhone 11', 'Pixel 2'])
def mobile_app(get_playwright, get_browser, request):
    if os.environ['PWBROWSER'] == 'firefox':
        pytest.skip()
    base_url = request.config.getini('base_url')
    device = request.param
    device_config = get_playwright.devices.get(device)
    if device_config is not None:
        device_config.update(BROWSER_OPTIONS)
    else:
        device_config = BROWSER_OPTIONS
    app = App(get_browser, base_url=base_url, **device_config)
    app.goto('/')
    yield app
    app.close()


@fixture(scope='session')
def mobile_app_auth(mobile_app, request):
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    mobile_app.goto('/login')
    mobile_app.login(**config)
    yield mobile_app


def pytest_addoption(parser):
    #parser.addoption('--base_url',action='store', default='http://localhost:8000/')
    parser.addoption('--secure', action='store', default='secure.json')
    parser.addoption('--device', action='store', default='')
    parser.addoption('--browser', action='store', default='chromium')
    parser.addini('base_url', help='base url of site under test', default='http://localhost:8000/')
    parser.addini('headless', help='run browser in headless mode', default='True')


def load_config(file):
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    with open(config_file) as cfg:
        return json.loads(cfg.read())
