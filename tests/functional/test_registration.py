from tests.functional import TestController
from skylines.model import User


class TestRegistration(TestController):
    def test_global_register_link(self):
        """User registration link is in the top bar"""

        # Check for link on start page
        link = self.browser.getLink(url='/users/new')
        assert link is not None, \
            'No registration link found on %s' % self.browser.url

    def test_register_button(self):
        """User registration link is in the login page"""

        # Check for link on login page
        self.browser.open('/login')
        link = self.browser.getLink(url='/users/new', index=1)
        assert link is not None, \
            'No registration link found on %s' % self.browser.url

    def open_and_fill_register_form(self, email, name, password,
                                    verify_password=None):
        if verify_password is None:
            verify_password = password

        # Open user registration page
        self.browser.open('/users/new')

        # Find registration form
        form = self.browser.getForm(index=2)

        form.getControl(name='email_address').value = email
        form.getControl(name='name').value = name
        form.getControl(name='password').value = password
        form.getControl(name='verify_password').value = verify_password

        return form

    def register_user(self, email, name, password, verify_password=None):
        form = self.open_and_fill_register_form(email, name, password,
                                                verify_password=verify_password)
        form.submit()

        user = User.by_email_address(email)
        assert user is not None, \
            "The user could not be found: %s" % email
        assert user.email_address == email
        assert user.name == name

    def expect_error(self, response,
                     email='expect_error@skylines-project.org',
                     name='Functional Test',
                     password='lambda',
                     verify_password=None,
                     check_user_exists=True):
        form = self.open_and_fill_register_form(email, name, password,
                                                verify_password=verify_password)
        form.submit()

        if check_user_exists:
            user = User.by_email_address(email)
            assert user is None, \
                "The user has been created by mistake: %s" % email

        assert response in self.browser.contents, \
            "String not found in response: %s\n%s" % \
            (response, self.browser.contents)

    def test_registration(self):
        """User registration works properly"""

        name = u'Functional Test'
        email = u'test_registration@skylines-project.org'
        self.register_user(email, name, password='lambda')

    def test_validation_errors(self):
        """Validation errors are working as expected"""

        self.expect_error('Please enter your email address', email='')
        self.expect_error('Invalid email address', email='abc')
        self.expect_error('Invalid email address', email='abc@')
        self.expect_error('Invalid email address', email='abc@de')
        self.expect_error('Invalid email address', email='abc@de.')

        self.expect_error('Please enter your name', name='')

        self.expect_error('Your password must have at least 6 characters',
                          password='abc')
        self.expect_error('Your passwords do not match',
                          password='lambda',
                          verify_password='lambda2')

    def test_duplicates(self):
        """Duplicate mail addresses are rejected"""
        email = 'test_duplicates@skylines-project.org'
        name = 'Duplicate Test'

        self.register_user(email, name, 'lambda')
        self.expect_error('A pilot with this email address exists already.',
                          email, name, 'lambda', check_user_exists=False)