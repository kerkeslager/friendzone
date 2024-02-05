import time
import unittest

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from webdriver_manager.firefox import GeckoDriverManager

class IntegrationTests(object):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not hasattr(cls, 'browser') or cls.browser is None:
            raise Exception("This is a base class and its tests should not run.")
        # WebDriverWait, che
        cls.wait = WebDriverWait(cls.browser, 5)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'browser') and cls.browser is not None:
            time.sleep(2)  # Keep the browser open for 2 seconds
            cls.browser.quit()
        super().tearDownClass()

    def find_url(self, *args, **kwargs):
        return self.live_server_url + reverse(*args, **kwargs)

    def test_login_success(self):
        # Navigate to the login page
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.browser.get(self.live_server_url + reverse('login'))

        # Fill in the username and password fields
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        # Submit the form
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Wait until the home page is loaded
        self.wait.until(EC.url_to_be(self.find_url('index')))

        # Assert that the browser redirects to the home page
        self.assertEqual(self.browser.current_url,  self.live_server_url + reverse('index'))

    def test_signup_success(self):
        self.browser.get(self.live_server_url + reverse('signup') )
        # Fill in the username and password fields
        username_input = self.browser.find_element(By.NAME, 'username')
        password1_input = self.browser.find_element(By.NAME, 'password1')
        password2_input = self.browser.find_element(By.NAME, 'password2')

        username_input.send_keys('newuser')
        password1_input.send_keys('newpassword12')
        password2_input.send_keys('newpassword12')

        # Submit the form
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Wait until the home page is loaded
        self.wait.until(EC.url_to_be(self.find_url('welcome')))

        # Assert that the browser redirects to the home page
        self.assertEqual(self.browser.current_url, self.find_url('welcome') )

class TestUserLoginChrome(IntegrationTests, StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        options = ChromeOptions()

        if settings.TEST_INTEGRATION_HEADLESS:
            options.add_argument('--headless=new')

        cls.browser = webdriver.Chrome(options)

        super().setUpClass()

class TestUserLoginFirefox(IntegrationTests, StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        options = FirefoxOptions()

        if settings.TEST_INTEGRATION_HEADLESS:
            options.headless = True

        cls.browser = webdriver.Firefox(
            options=options,
            service=FirefoxService(GeckoDriverManager().install()),
        )

        super().setUpClass()
