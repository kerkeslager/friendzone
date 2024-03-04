import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from webdriver_manager.firefox import GeckoDriverManager

from selenium.common.exceptions import NoSuchElementException

def find_e_with_retry(driver, by, value, attempts=10, delay=2):
    for attempt in range(attempts):
        try:
            return driver.find_element(by, value)
        except NoSuchElementException:
            if attempt < attempts - 1:
                time.sleep(delay)  # Wait for a bit before retrying
            else:
                print(f"Could not find element {value}")
                print(driver.page_source)
                raise Exception("Could not find element")


class IntegrationTests(object):
    '''
    Write integration tests in this base class.

    All tests will be inherited by the ChromeIntegrationTests and
    FirefoxIntegrationTests classes. The tests on this base class won't
    run because it doesn't inherit from TestCase. But ChromeIntegrationTests
    and FirefoxIntegrationTests DO inherit from TestCase (indirectly), so
    the test_-prefixed methods they inherit from this base class will be run.

    The purpose of all this is to let us write tests once on this base class
    and have them run twice, once on Chrome and once on Firefox.
    This way we don't have to write two tests for every integration feature.
    '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Subclasses should set cls.browser
        assert getattr(cls, 'browser') is not None

        cls.wait = WebDriverWait(cls.browser, 20)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        if getattr(cls, 'browser') is not None:
            cls.browser.quit()

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
        self.browser.get(self.live_server_url + reverse('signup'))
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
        self.assertEqual(self.browser.current_url, self.find_url('welcome'))

    def test_post_visibility(self):
        # Create three users
        User = get_user_model()
        user0 = User.objects.create_user(
            username='user0', password='password0')
        user1 = User.objects.create_user(
            username='user1', password='password1')
        user2 = User.objects.create_user(
            username='user2', password='password2')

        # Make users 0 and 1 Friends
        invitation = user0.create_invitation(
            circles=user0.circles.filter(name='Friends'),
        )
        user1.accept_invitation(
            invitation,
            circles=user1.circles.filter(name='Friends'),
        )

        # Make users 0 and 2 Family
        invitation = user0.create_invitation(
            circles=user0.circles.filter(name='Family'),
        )
        user2.accept_invitation(
            invitation,
            circles=user2.circles.filter(name='Family'),
        )

        # Log in as user 0
        self.browser.get(self.live_server_url + reverse('login'))
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user0')
        password_input.send_keys('password0')
        submit_button = self.browser.find_element(
            By.XPATH,
            '//button[@type="submit"]',
        )
        submit_button.click()

        # Publish a post to Friends
        # Checkbox input for circle

        form_xpath = '//form[@action="{}"]'.format(reverse('post_create'))
        checkbox_parent_xpath = "//label[contains(., 'Friends')]"
        checkbox_xpath = "//input[@type='checkbox']"
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '{}{}'.format(form_xpath, checkbox_parent_xpath))))
        checkbox = self.browser.find_element(
            By.XPATH,
            '{}{}{}'.format(
                form_xpath,
                checkbox_parent_xpath,
                checkbox_xpath,
            ),
        )
        checkbox.click()

        post_input = self.browser.find_element(By.NAME, 'text')
        post_input.send_keys('This is a test post for Friends')

        create_button = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'create')]")))
        create_button.click()

        self.wait.until(EC.text_to_be_present_in_element(
            (By.CLASS_NAME, 'post'), 'This is a test post for Friends'))

        # Log out as user 0, Post is created by create_button click and shown
        # in the post feed
        logout_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        logout_button.click()

        self.browser.get(self.live_server_url + reverse('logout'))

        # Log in as user 1
        self.browser.find_element(By.LINK_TEXT, "login").click()
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user1')
        password_input.send_keys('password1')
        submit_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Verify that user 1 can view the post
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'post'),
                'This is a test post for Friends',
            ),
        )

        # Log out as user 1
        logout_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        logout_button.click()

        # Log in as user 2
        self.browser.find_element(By.LINK_TEXT, "login").click()
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user2')
        password_input.send_keys('password2')
        submit_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Verify that user 2 CANNOT view the post
        self.wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'post')))

    def test_post_circles_prechecked_on_edit(self):
        User = get_user_model()
        user0 = User.objects.create_user(
            username='user0', password='password0')

        # Log in as user 0
        self.browser.get(self.live_server_url + reverse('login'))
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user0')
        password_input.send_keys('password0')
        submit_button = self.browser.find_element(
            By.XPATH,
            '//button[@type="submit"]',
        )
        submit_button.click()

        # Publish a post to Friends
        # Checkbox input for circle

        form_xpath = '//form[@action="{}"]'.format(reverse('post_create'))
        checkbox_parent_xpath = "//label[contains(., 'Friends')]"
        checkbox_xpath = "//input[@type='checkbox']"
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '{}{}'.format(form_xpath, checkbox_parent_xpath))))
        checkbox = self.browser.find_element(
            By.XPATH,
            '{}{}{}'.format(
                form_xpath,
                checkbox_parent_xpath,
                checkbox_xpath,
            ),
        )
        checkbox.click()

        post_input = self.browser.find_element(By.NAME, 'text')
        post_input.send_keys('This is a test post for Friends')

        create_button = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'create')]")))
        create_button.click()

        self.browser.find_element(By.LINK_TEXT, "View").click()
        self.browser.find_element(By.LINK_TEXT, "Edit").click()
        friends_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Friends']")
        friends_circle_checkbox = friends_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        self.assertTrue(
            friends_circle_checkbox.is_selected(),
            "Circle 1 should be pre-checked.")

    def test_post_visibility_after_post_edit(self):
        # Create three users
        User = get_user_model()
        user0 = User.objects.create_user(
            username='user0', password='password0')
        user1 = User.objects.create_user(
            username='user1', password='password1')
        user2 = User.objects.create_user(
            username='user2', password='password2')

        # Make users 0 and 1 Friends
        invitation = user0.create_invitation(
            circles=user0.circles.filter(name='Friends'),
        )
        user1.accept_invitation(
            invitation,
            circles=user1.circles.filter(name='Friends'),
        )

        # Make users 0 and 2 Family
        invitation = user0.create_invitation(
            circles=user0.circles.filter(name='Family'),
        )
        user2.accept_invitation(
            invitation,
            circles=user2.circles.filter(name='Family'),
        )

        # Log in as user 0
        self.browser.get(self.live_server_url + reverse('login'))
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user0')
        password_input.send_keys('password0')
        submit_button = self.browser.find_element(
            By.XPATH,
            '//button[@type="submit"]',
        )
        submit_button.click()

        # Publish a post to Friends
        # Checkbox input for circle

        form_xpath = '//form[@action="{}"]'.format(reverse('post_create'))
        checkbox_parent_xpath = "//label[contains(., 'Friends')]"
        checkbox_xpath = "//input[@type='checkbox']"
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '{}{}'.format(form_xpath, checkbox_parent_xpath))))
        checkbox = self.browser.find_element(
            By.XPATH,
            '{}{}{}'.format(
                form_xpath,
                checkbox_parent_xpath,
                checkbox_xpath,
            ),
        )
        checkbox.click()

        post_input = self.browser.find_element(By.NAME, 'text')
        post_input.send_keys('This is a test post for Friends')

        create_button = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'create')]")))
        create_button.click()

        self.browser.find_element(By.LINK_TEXT, "View").click()
        self.browser.find_element(By.LINK_TEXT, "Edit").click()

        post_input = self.browser.find_element(By.NAME, 'text')
        post_input.clear()
        post_input.send_keys('This is a test post for Family')

        friends_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Friends']")
        friends_circle_checkbox = friends_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        friends_circle_checkbox.click()

        self.assertFalse(
            friends_circle_checkbox.is_selected(),
            "Circle should not be checked.")

        family_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Family']")
        family_circle_checkbox = family_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        family_circle_checkbox.click()

        self.assertTrue(
            family_circle_checkbox.is_selected(),
            "Circle Family show now be checked.")

        update_button = self.browser.find_element(
            By.XPATH, "//button[contains(text(), 'save')]")
        update_button.click()

        # Log out as user 0, Post is created by create_button click and shown
        # in the post feed
        logout_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        logout_button.click()

        self.browser.get(self.live_server_url + reverse('logout'))

        # Log in as user 1
        self.browser.find_element(By.LINK_TEXT, "login").click()
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user1')
        password_input.send_keys('password1')
        submit_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Verify that user 1 cannot view the post
        self.wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'post')))

        # Log out as user 1
        logout_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        logout_button.click()

        # Log in as user 2
        self.browser.find_element(By.LINK_TEXT, "login").click()
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user2')
        password_input.send_keys('password2')
        submit_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Verify that user 2 CAN view the post

        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'post'),
                'This is a test post for Family',
            ),
        )

    def test_visible_to_all_after_edit_post(self):
        # Create three users
        User = get_user_model()
        user0 = User.objects.create_user(
            username='user0', password='password0')
        user1 = User.objects.create_user(
            username='user1', password='password1')
        user2 = User.objects.create_user(
            username='user2', password='password2')

        # Make users 0 and 1 Friends
        invitation = user0.create_invitation(
            circles=user0.circles.filter(name='Friends'),
        )
        user1.accept_invitation(
            invitation,
            circles=user1.circles.filter(name='Friends'),
        )

        # Make users 0 and 2 Family
        invitation = user0.create_invitation(
            circles=user0.circles.filter(name='Family'),
        )
        user2.accept_invitation(
            invitation,
            circles=user2.circles.filter(name='Family'),
        )

        # Log in as user 0
        self.browser.get(self.live_server_url + reverse('login'))
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user0')
        password_input.send_keys('password0')
        submit_button = self.browser.find_element(
            By.XPATH,
            '//button[@type="submit"]',
        )
        submit_button.click()

        # Publish a post to Friends
        # Could add a verification that after reload, User 0 can see the post
        # editted properly

        form_xpath = '//form[@action="{}"]'.format(reverse('post_create'))
        checkbox_parent_xpath = "//label[contains(., 'Friends')]"
        checkbox_xpath = "//input[@type='checkbox']"
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '{}{}'.format(form_xpath, checkbox_parent_xpath))))
        checkbox = self.browser.find_element(
            By.XPATH,
            '{}{}{}'.format(
                form_xpath,
                checkbox_parent_xpath,
                checkbox_xpath,
            ),
        )
        checkbox.click()

        post_input = self.browser.find_element(By.NAME, 'text')
        post_input.send_keys('This is a test post for Friends')

        create_button = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'create')]")))
        create_button.click()

        self.browser.find_element(By.LINK_TEXT, "View").click()
        self.browser.find_element(By.LINK_TEXT, "Edit").click()

        post_input = self.browser.find_element(By.NAME, 'text')
        post_input.clear()
        post_input.send_keys('This is a test post for Friends and Family')

        friends_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Friends']")
        friends_circle_checkbox = friends_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        self.assertTrue(
            friends_circle_checkbox.is_selected(),
            "Circle Friends should still be checked.")

        family_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Family']")
        family_circle_checkbox = family_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")
        family_circle_checkbox.click()

        self.assertTrue(
            family_circle_checkbox.is_selected(),
            "Circle 2 should now be checked.")

        update_button = self.browser.find_element(
            By.XPATH, "//button[contains(text(), 'save')]")
        update_button.click()

        # Log out as user 0, Post is created by create_button click and shown
        # in the post feed
        logout_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        logout_button.click()

        self.browser.get(self.live_server_url + reverse('logout'))

        # Log in as user 1
        self.browser.find_element(By.LINK_TEXT, "login").click()
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user1')
        password_input.send_keys('password1')
        submit_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Verify that user 1 CAN view the post
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'post'),
                'This is a test post for Friends and Family',
            ),
        )

        # Log out as user 1
        logout_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        logout_button.click()

        # Log in as user 2
        self.browser.find_element(By.LINK_TEXT, "login").click()
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user2')
        password_input.send_keys('password2')
        submit_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Verify that user 2 CAN view the post

        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'post'),
                'This is a test post for Friends and Family',
            ),
        )

    def test_invitation_process(self):
        # Create two users
        User = get_user_model()
        user0 = User.objects.create_user(
            username='user0', password='password0')
        user1 = User.objects.create_user(
            username='user1', password='password1')

        # Log in as user 0
        self.browser.get(self.live_server_url + reverse('login'))
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user0')
        password_input.send_keys('password0')
        submit_button = self.browser.find_element(
            By.XPATH,
            '//button[@type="submit"]',
        )
        submit_button.click()

        # Create an invitation
        self.browser.get(self.live_server_url + reverse('invite_create'))
        # time.sleep(20)
        # Fill in the form
        name_input = self.browser.find_element(By.NAME, 'name')
        name_input.send_keys('Test Invitation')

        message_input = self.browser.find_element(By.NAME, 'message')
        message_input.send_keys('This is a test invitation message.')
        # time.sleep(20)
        # Selecting a circle (e.g., 'Friends')
        # This assumes you know the value or can identify the checkbox for the
        # 'Friends' circle.
        family_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Family']")
        family_circle_checkbox = family_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")
        family_circle_checkbox.click()

        cb = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'save')]")))
        self.browser.execute_script("arguments[0].scrollIntoView();", cb)
        cb.click()
        invite_link = self.browser.find_element(
            By.LINK_TEXT, "Test Invitation")

        # Extract the href attribute to get the URL
        invitation_url = invite_link.get_attribute('href')

        # Output the extracted URL (for demonstration purposes)
        # print("Extracted Invitation URL:", invitation_url)

        # Log out as user 0
        logout_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        logout_button.click()

        # Log in as user 1
        self.browser.find_element(By.LINK_TEXT, "login").click()
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user1')
        password_input.send_keys('password1')
        submit_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Accept the invitation
        self.browser.get(invitation_url)

        family_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Family']")
        family_circle_checkbox = family_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")
        family_circle_checkbox.click()

        friends_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Friends']")
        friends_circle_checkbox = friends_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        self.assertTrue(
            family_circle_checkbox.is_selected(),
            "Circle 1 should be checked.")

        self.assertFalse(
            friends_circle_checkbox.is_selected(),
            "User 1 should not have Friends circle pre-checked.")

        accept_button = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'accept')]")))
        accept_button.click()

        # Verify that user 1 can view user 0's profile page
        self.wait.until(EC.text_to_be_present_in_element(
            (By.TAG_NAME, 'h1'),
            user0.username,
        ))

        family_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Family']")
        family_circle_checkbox = family_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        friends_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Friends']")
        friends_circle_checkbox = friends_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")
        self.assertTrue(
            family_circle_checkbox.is_selected(),
            "Circle 1 should be checked.")

        self.assertFalse(
            friends_circle_checkbox.is_selected(),
            "Circle 2 should be pre-checked.")

        # Log out as user 1
        logout_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        logout_button.click()

        # Log in as user 0
        self.browser.find_element(By.LINK_TEXT, "login").click()
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user0')
        password_input.send_keys('password0')
        submit_button = self.browser.find_element(
            By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Verify that user 0 can view user 1's profile page
        self.browser.get(
            self.live_server_url + reverse(
                'user_detail',
                args=[
                    user1.id]))
        self.wait.until(EC.text_to_be_present_in_element(
            (By.TAG_NAME, 'h1'),
            user1.username,
        ))

        family_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Family']")
        family_circle_checkbox = family_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        friends_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Friends']")
        friends_circle_checkbox = friends_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        self.assertTrue(
            family_circle_checkbox.is_selected(),
            "Circle 1 should be pre-checked.")
        self.assertFalse(
            friends_circle_checkbox.is_selected(),
            "Circle 2 should be pre-checked.")

    def test_invitation_circles_prechecked_on_edit(self):
        User = get_user_model()
        user0 = User.objects.create_user(
            username='user0', password='password0')

        # Log in as user 0
        self.browser.get(self.live_server_url + reverse('login'))
        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')
        username_input.send_keys('user0')
        password_input.send_keys('password0')
        submit_button = self.browser.find_element(
            By.XPATH,
            '//button[@type="submit"]',
        )
        submit_button.click()

        # Create an invitation
        self.browser.get(self.live_server_url + reverse('invite_create'))

        # Fill in the form
        name_input = self.browser.find_element(By.NAME, 'name')
        name_input.send_keys('Test Invitation')

        message_input = self.browser.find_element(By.NAME, 'message')
        message_input.send_keys('This is a test invitation message.')

        # Selecting a circle (e.g., 'Friends')

        family_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Family']")
        family_circle_checkbox = family_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")
        family_circle_checkbox.click()

        cb = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'save')]")))
        self.browser.execute_script("arguments[0].scrollIntoView();", cb)
        cb.click()

        invite_link = self.browser.find_element(
            By.LINK_TEXT, "Test Invitation")
        invitation_url = invite_link.get_attribute('href')

        self.browser.get(invitation_url)

        edit_link = self.browser.find_element(
            By.LINK_TEXT, "edit")
        edit_url = edit_link.get_attribute('href')
        self.browser.get(edit_url)

        family_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Family']")
        family_circle_checkbox = family_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        friends_circle_label = self.browser.find_element(
            By.XPATH, "//label[normalize-space()='Friends']")
        friends_circle_checkbox = friends_circle_label.find_element(
            By.XPATH, ".//preceding-sibling::input[@type='checkbox']")

        self.assertTrue(
            family_circle_checkbox.is_selected(),
            "Circle 1 should be pre-checked.")
        self.assertFalse(
            friends_circle_checkbox.is_selected(),
            "Circle 2 should be pre-checked.")


@tag('slow')
class ChromeIntegrationTests(IntegrationTests, StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        options = ChromeOptions()

        options.page_load_strategy = 'normal'

        if settings.TEST_INTEGRATION_HEADLESS:
            options.add_argument('--headless=new')

            # The default window is very small which causes footer to cover
            # buttons which we want to click, causing tests to fail.
            options.add_argument('--window-size=1920,1080')

        s = Service(ChromeDriverManager().install())
        cls.browser = webdriver.Chrome(service=s, options=options)

        super().setUpClass()


@tag('slow')
class FirefoxIntegrationTests(IntegrationTests, StaticLiveServerTestCase):
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
