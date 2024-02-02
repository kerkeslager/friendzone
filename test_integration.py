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
        # WebDriverWait, che
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



    ## With signing up, if I set up the signup_url to be reverse('signup'), I'm currently going from the 
    # Login test success logged in as testuser. auth/login takes me to to home_url which is index.    
    # I'm not sure if I should be testing the signup page in the same test as the login page.
    # Well, I'm accessing the signup page from the login page going from auth/login to auth/signup... Seems like bad practice 
    # Check below for how we might check for a failed signup.
    def test_signup_success(self):
        # Navigate to the signup page
        self.home_url = self.live_server_url + reverse('welcome')  # 'home' is the name of your post-login redirect URL
        self.signup_url = self.live_server_url + reverse('signup')  # 'signup' is the name of your signup URL
        self.browser.get(self.signup_url)
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
        self.wait.until(EC.url_to_be(self.home_url))

        # Assert that the browser redirects to the home page
        self.assertEqual(self.browser.current_url, self.home_url)



    # The exceptions are currently text inputs that I might have to search for in the browser such as:
    # user with this username already exists
    # how might we deal with this?
    '''
    def test_signup_failure(self):
        # Navigate to the signup page
        self.home_url = self.live_server_url + reverse('welcome')  # 'home' is the name of your post-login redirect URL
        self.signup_url = self.live_server_url + reverse('signup')  # 'signup' is the name of your signup URL
        self.browser.get(self.signup_url)
        # Fill in the username and password fields
        username_input = self.browser.find_element(By.NAME, 'username')
        password1_input = self.browser.find_element(By.NAME, 'password1')
        password2_input = self.browser.find_element(By.NAME, 'password2')

        username_input.send_keys('testuser')
        password1_input.send_keys('testpassword')
        password2_input.send_keys('testpassword')

        # Submit the form
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Wait until the home page is loaded
        self.wait.until(EC.url_to_be(self.home_url))

        # Assert that the browser redirects to the home page
        self.assertEqual(self.browser.current_url, self.home_url)
    '''


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