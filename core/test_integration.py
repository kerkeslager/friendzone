from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time 
    
class TestUserLogin(StaticLiveServerTestCase):
    '''
    #Using ChromeDriver
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()
        cls.browser.implicitly_wait(10)
        #cls.wait = WebDriverWait(cls.browser, 10)
        cls.wait = WebDriverWait(cls.browser, 50)  # Increase wait time to 20 seconds
    '''
    

    @classmethod
    def setUpClass(cls):
        # Setup code to run once before all tests, e.g., starting a browser
        cls.browser = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        cls.browser.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.browser, 10)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        time.sleep(5)  # Keep the browser open for 5 seconds
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        # Setup code to run before each test, e.g., creating test data
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = self.live_server_url + reverse('login')  # 'login' is the name of your login URL
        self.home_url = self.live_server_url + reverse('index')  # 'home' is the name of your post-login redirect URL

    def test_login_success(self):
        # Navigate to the login page
        self.browser.get(self.login_url)

        # Fill in the username and password fields
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        # Submit the form
        #submit_button = self.browser.find_element(By.ID, 'submit')
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Wait until the home page is loaded
        
        
        self.wait.until(EC.url_to_be(self.home_url))
        # Assert that the browser redirects to the home page
        self.assertEqual(self.browser.current_url, self.home_url)

# Add more tests 
