from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService 
from webdriver_manager.firefox import GeckoDriverManager
import time 
import unittest

class IntegrationTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not hasattr(cls, 'browser') or cls.browser is None:
            raise unittest.SkipTest("Browser not initialized. Skipping tests in BaseTestUserLogin.")
        # WebDriverWait, check  there is a page load timeout so it doesn't hang forever 
        cls.wait = WebDriverWait(cls.browser, 5)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'browser') and cls.browser is not None:
            time.sleep(2)  # Keep the browser open for 2 seconds
            cls.browser.quit()
        super().tearDownClass()


    def test_login_success(self):
        # Navigate to the login page
        User = get_user_model()
        self.login_url = self.live_server_url + reverse('login')  # 'login' is the name of your login URL
        self.home_url = self.live_server_url + reverse('index')  # 'home' is the name of your post-login redirect URL
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.browser.get(self.login_url)

        # Fill in the username and password fields
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        # Submit the form
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Wait until the home page is loaded
        self.wait.until(EC.url_to_be(self.home_url))

        # Assert that the browser redirects to the home page
        self.assertEqual(self.browser.current_url, self.home_url)

class TestUserLoginChrome(IntegrationTests):
    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Chrome()
        super().setUpClass()

class TestUserLoginFirefox(IntegrationTests):
    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        super().setUpClass()