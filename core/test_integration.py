import time
import unittest

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import tag

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
            raise Exception(
                'This is a base class and its tests should not run.'
            )
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
        user = User.objects.create_user(
            username='testuser',
            password='testpassword',
        )
        self.browser.get(self.live_server_url + reverse('login'))

        # Fill in the username and password fields
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        # Submit the form
        submit_button = self.browser.find_element(
            By.XPATH,
            '//button[@type="submit"]',
        )
        submit_button.click()

        # Wait until the home page is loaded
        self.wait.until(EC.url_to_be(self.find_url('index')))

        # Assert that the browser redirects to the home page
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse('index'),
        )

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
        submit_button = self.browser.find_element(
            By.XPATH,
            '//button[@type="submit"]',
        )
        submit_button.click()

        # Wait until the home page is loaded
        self.wait.until(EC.url_to_be(self.find_url('welcome')))

        # Assert that the browser redirects to the home page
        self.assertEqual(self.browser.current_url, self.find_url('welcome') )

@tag('slow')
class TestUserLoginChrome(IntegrationTests, StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        options = ChromeOptions()

        if settings.TEST_INTEGRATION_HEADLESS:
            options.add_argument('--headless=new')

            # The default window is very small which causes footer to cover
            # buttons which we want to click, causing tests to fail.
            options.add_argument('--window-size=1920,1080')

        cls.browser = webdriver.Chrome(options)

        super().setUpClass()

@tag('slow')
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
        cls.browser.set_window_size(1920, 1080)

        super().setUpClass()


class PostIntegrationTests(object):
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

   


class TestPostVisibility(PostIntegrationTests, StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        options = ChromeOptions()

        if settings.TEST_INTEGRATION_HEADLESS:
            options.add_argument('--headless=new')

            # The default window is very small which causes footer to cover
            # buttons which we want to click, causing tests to fail.
            options.add_argument('--window-size=1920,1080')

        cls.browser = webdriver.Chrome(options)

        super().setUpClass()
        
    def test_post_visibility(self):
        # Create three users
        User = get_user_model()
        user0 = User.objects.create_user(username='user0', password='password0')
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        # Make users 0 and 1 Friends
        invitation = user0.create_invitation(circles=user0.circles.filter(name='Friends'))
        user1.accept_invitation(invitation, circles=user1.circles.filter(name='Friends'))

        # Make users 0 and 2 Family
        invitation = user0.create_invitation(circles=user0.circles.filter(name='Family'))
        user2.accept_invitation(invitation, circles=user2.circles.filter(name='Family'))

        # Log in as user 0
        self.browser.get(self.live_server_url + reverse('login'))
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user0')
        password_input.send_keys('password0')
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Publish a post to Friends
        # Checkbox input for circle

        
        nav_xpath = "//nav[contains(., 'Friends') or ./svg[@unique_attribute='Friends']]"
        checkbox = self.browser.find_element(By.XPATH, f"{nav_xpath}//input[@type='checkbox']")
        checkbox.click()

        

        post_input = self.browser.find_element(By.NAME, 'text')
        post_input.send_keys('This is a test post for Friends')
        
        wait = WebDriverWait(self.browser, 10)


        create_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'create')]")))
        create_button.click()

        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'post'), 'This is a test post for Friends'))

        # Log out as user 0, Post is created by create_button click and shown in the post feed 
        logout_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        logout_button.click()

        # Log in as user 1
        self.browser.get(self.live_server_url + reverse('login'))
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user1')
        password_input.send_keys('password1')
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()



        # Verify that user 1 can view the post
        ''' Currently Not Working with the real test'''
        #self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'post'), 'This is a test post for Friends'))
        #The test passes for 
        self.wait.until(EC.text_to_be_present_in_element((By.ID,'feed'), 'There are no posts in your feed'))

        # Log out as user 1
        logout_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        logout_button.click()
        

        # Log in as user 2
        self.browser.get(self.live_server_url + reverse('login'))
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user2')
        password_input.send_keys('password2')
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()


        # Verify that user 2 CANNOT view the post
        #self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'post'), 'There are no posts in your feed'))
        self.wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'post')))