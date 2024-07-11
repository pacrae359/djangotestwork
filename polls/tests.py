import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm, CreatePollForm

from .views import loginPage
from .models import Question, Choice

# Create your tests here.

def create_question(question_text, days):
	"""
	Create a question with the given 'question_text' and published the
	given number of 'days' offset to now (negative for questions published 
	in the past, positive for questions that have yet to be published).
	"""
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(choice_text,question_id):
	"""
	Creates a choice for use with the above question method such that tests will not fail, and can be used
	to test if excluding questions with choices is working as intended.
	"""
	return Choice.objects.create(choice_text=choice_text, question_id=question_id)

class QuestionIndexViewTests(TestCase):

	def test_no_questions(self):
		"""
		If no questions exist, an appropriate message is displayed.
		"""
		response = self.client.get(reverse("polls:index"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		#this checks if the response list of questions is equal to an empty list in the instance no question is present.
		self.assertQuerySetEqual(
			response.context["latest_question_list"], 
			[])

	def test_past_question(self):
		"""
		Questions with pub_date in the past are displayed on the
		index page.
		"""
		question = create_question(question_text="Past question.", days=-30)
		create_choice("Choice.", question.id)
		response =  self.client.get(reverse("polls:index"))
		self.assertQuerySetEqual(
			response.context["latest_question_list"],
			[question],
		)

	def test_future_question(self):
		"""
		Question with a pub_date in the future aren't displayed on
		the index page.
		"""
		question1 = create_question(question_text="Future question.", days=30)
		create_choice("Choice.", question1.id)
		response = self.client.get(reverse("polls:index"))
		self.assertContains(response, "No polls are available")
		self.assertQuerySetEqual(
			response.context["latest_question_list"],
			[],
		)
	def test_future_question_and_past_question(self):
		"""
		Even if both past and future questions exist, only past questions
		are displayed.
		"""
		question = create_question(question_text="Past question.", days=-30)
		question2 = create_question(question_text="Future question.", days=30)
		create_choice("Choice.", question.id)
		create_choice("Choice.", question2.id)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerySetEqual(
			response.context["latest_question_list"],
			[question],
		)

	def test_two_past_question(self):
		"""
		The questions index page may display multiple questions.
		"""
		question1 = create_question(question_text="Past question 1.", days=-30)
		question2 = create_question(question_text="Past question 2.", days=-7)
		create_choice("Choice.", question1.id)
		create_choice("Choice.", question2.id)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerySetEqual(
			response.context["latest_question_list"],
			[question2, question1],
		)

	def test_question_with_no_choices(self):
		"""
		The questions index page will not show questions that do not have any choices. Only testing past questions as future questions should never be shown
		due to earlier testing.
		"""
		question = create_question(question_text="Question without choices", days=-30)
		response = self.client.get(reverse("polls:index"))
		self.assertContains(response, "No polls are available")
		self.assertQuerySetEqual(response.context["latest_question_list"],
			[],
		)

	def test_question_with_and_question_without_choices(self):
		"""
		The questions page will exclude questions without choices and show those with choices. Only testing past questions as future questions should never be shown
		due to earlier testing.
		"""
		question_no_choice = create_question(question_text="Question without choices", days=-30)
		question_with_choice = create_question(question_text="Question with choices", days=-30)
		create_choice("Choice", question_with_choice.id)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerySetEqual(
			response.context["latest_question_list"],
			[question_with_choice],
		)

	def test_admin_shown_past_and_future_questions(self):
		"""
		If the user is a logged in admin, then both future and past questions should be displayed to them.
		"""
		admin_password = "test_password"
		my_admin = User.objects.create_superuser('testuser', 'myemail@test.com', admin_password)
		self.client.login(username=my_admin.username, password=admin_password)
		question1 = create_question(question_text="Past Question", days=-30)
		question2 = create_question(question_text="Future Question", days=30)
		create_choice("Choice.", question1.id)
		create_choice("Choice.", question2.id)
		response = self.client.get(reverse("polls:index"))
		self.assertQuerySetEqual(
			response.context["latest_question_list"],
			[question2,question1],
		)


class QuestionDetailViewTests(TestCase):

	def test_past_question(self):
		past_question = create_question(question_text="Past Question.", days=-5)
		create_choice("Choice.", past_question.id)
		url = reverse("polls:detail", args=(past_question.id,))
		response = self.client.get(url)
		self.assertContains(response, past_question.question_text)

	def test_future_question(self):
		future_question = create_question(question_text="Future Question.", days=5)
		create_choice("Choice.", future_question.id)
		url = reverse("polls:detail", args=(future_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_question_with_no_choices(self):
		"""
		The questions detail page will not show questions that do not have any choices. Only testing past questions as future questions should never be shown
		due to earlier testing.
		"""
		question = create_question(question_text="Question without choices", days=-30)
		response = self.client.get(reverse("polls:detail", args=(question.id,)))
		self.assertEquals(response.status_code, 404)

	def test_admin_future_question(self):
		"""
		An admin should be able to access the details pages of questions.
		"""
		admin_password = "test_password"
		my_admin = User.objects.create_superuser('testuser', 'myemail@test.com', admin_password)
		self.client.login(username=my_admin.username, password=admin_password)
		question = create_question(question_text="Future Question", days=30)
		create_choice("Choice.", question.id)
		response = self.client.get(reverse("polls:detail", args=(question.id,)))
		self.assertContains(response, question.question_text)


class QuestionResultsViewTests(TestCase):

	def test_past_question(self):
		past_question = create_question(question_text="Past Question.", days=-5)
		create_choice("Choice.", past_question.id)
		url = reverse("polls:results", args=(past_question.id,))
		response = self.client.get(url)
		self.assertContains(response, past_question.question_text)

	def test_future_question(self):
		future_question = create_question(question_text="Future Question.", days=5)
		create_choice("Choice.", future_question.id)
		url = reverse("polls:results", args=(future_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_question_with_no_choices(self):
		"""
		The questions index page will not show questions that do not have any choices. Only testing past questions as future questions should never be shown
		due to earlier testing.
		"""
		question = create_question(question_text="Question without choices", days=-30)
		response = self.client.get(reverse("polls:results", args=(question.id,)))
		self.assertEquals(response.status_code, 404)

	def test_admin_future_question(self):
		"""
		An admin should be able to access the results pages of future questions.
		"""
		admin_password = "test_password"
		my_admin = User.objects.create_superuser('testuser', 'myemail@test.com', admin_password)
		self.client.login(username=my_admin.username, password=admin_password)
		question = create_question(question_text="Future Question", days=30)
		create_choice("Choice.", question.id)
		response = self.client.get(reverse("polls:results", args=(question.id,)))
		self.assertContains(response, question.question_text)

class LoginViewTests(TestCase):

	def test_login_form_existing_user(self):
		"""
		This tests if the form properly allows logging in for an existing user.
		"""	
		user_data = {'username': 'test', 'password': 'testpass'}
		User.objects.create_user(username='test',password='testpass')
		response = self.client.post(reverse("polls:login"), user_data, follow=True)
		self.assertTrue(response.context["user"].is_active)

	def test_incorrect_credentials(self):
		"""
		This test checks if the user is given the correct error message and NOT logged in when giving incorrect/non-existent credentials.
		"""
		user_data = {'username': 'test', 'password': 'testpass'}
		response = self.client.post(reverse("polls:login"), user_data, follow=True)
		self.assertContains(response, "This Username and Password combination is not recognised.")
		
	def test_logged_in_access(self):
		"""
		This test ensures logged in users cannot access the login page by sniping the URL.
		"""
		user = User.objects.create_user(username='test',password='testpass')
		username='test'
		password='testpass'
		self.client.login(username=username,password=password)
		response = self.client.get(reverse("polls:login"))
		self.assertTemplateNotUsed(reverse('polls:login'))

class RegisterViewTests(TestCase):

	def test_register_form(self):
		"""
		This tests if the register form functions correctly when given valid data
		"""
		username = 'user'
		password = 'testingpassword123'
		user_data = {'username': 'user', 'email': 'email@email.com','password1':'testingpassword123', 'password2': 'testingpassword123'}
		response = self.client.post(reverse("polls:register"), user_data, follow=True)
		user_data = {"username": username, "password": password}
		response = self.client.post(reverse("polls:login"), user_data, follow=True)
		self.assertTrue(response.context["user"].is_active)

	def test_register_form_no_username(self):
		"""
		This test will check whether the registration form will not go through when not provided with a username.
		"""
		user_data = {'username': '', 'email': 'email@email.com','password1':'testingpassword123', 'password2': 'testingpassword123'}
		response = self.client.post(reverse("polls:register"), user_data, follow=True)
		self.assertTemplateNotUsed(reverse("polls:login"))
		form = CreateUserForm(user_data)
		self.assertFalse(form.is_valid())

	def test_register_form_passwords_not_matching(self):
		"""
		This test will check whether the registration form will not work if passwords provided do not match. 
		"""
		user_data = {'username': 'user', 'email': 'email@email.com','password1':'testingpassword', 'password2': 'testingpassword123'}
		response = self.client.post(reverse("polls:register"), user_data, follow=True)
		self.assertTemplateNotUsed(reverse("polls:login"))
		form = CreateUserForm(user_data)
		self.assertFalse(form.is_valid())

	def test_register_form_blank_password(self):
		"""
		This test will check whether the registration form will not work if there is no password provided.
		"""
		user_data = {'username': 'user', 'email': 'email@email.com','password1':'', 'password2': ''}
		response = self.client.post(reverse("polls:register"), user_data, follow=True)
		self.assertTemplateNotUsed(reverse("polls:login"))
		form = CreateUserForm(user_data)
		self.assertFalse(form.is_valid())

	def test_register_form_no_email(self):
		"""
		This test checks if the registration form will allow a blank email field.
		"""
		user_data = {'username': 'user', 'email': '','password1':'testingpassword123', 'password2': 'testingpassword123'}
		response = self.client.post(reverse("polls:register"), user_data, follow=True)
		self.assertTemplateNotUsed(reverse("polls:login"))
		form = CreateUserForm(user_data)
		self.assertFalse(form.is_valid())

class CreatePollViewTests(TestCase):

	def test_not_logged_in_access(self):
		"""
		This tests if it's possible to access the create poll page when not logged in (Which it shouldn't be!)
		"""
		response = self.client.get(reverse("polls:createpoll"))
		self.assertTemplateNotUsed("polls:createpoll")

	def test_logged_in_access(self):
		"""
		This tests if the user can access the poll creation page when logged in.
		"""
		user = User.objects.create_user(username='test',password='testpass')
		username='test'
		password='testpass'
		self.client.login(username=username,password=password)
		response = self.client.get(reverse("polls:createpoll"))
		self.assertTemplateUsed(reverse("polls:createpoll"))

	def test_create_question_no_question(self):
		"""
		This tests if the create poll page will create a poll that has no poll text.
		"""
		user = User.objects.create_user(username='test',password='testpass')
		username='test'
		password='testpass'
		self.client.login(username=username,password=password)
		poll_data = {'poll_name': '', 'poll_pub_date': timezone.now(), 'poll_answer1':'Answer1', 'poll_answer2':'Answer2', 'poll_answer3':'Answer3'}
		response = self.client.post(reverse("polls:createpoll"), poll_data, follow=True)
		form = CreatePollForm(poll_data)
		self.assertFalse(form.is_valid())

	def test_create_question_no_choices(self):
		"""
		This test checks if a poll can be published without having any choices associated with it.
		"""
		user = User.objects.create_user(username='test',password='testpass')
		username='test'
		password='testpass'
		self.client.login(username=username,password=password)
		poll_data = {'poll_name': 'Poll Text', 'poll_pub_date': timezone.now(), 'poll_answer1':'', 'poll_answer2':'', 'poll_answer3':''}
		response = self.client.post(reverse("polls:createpoll"), poll_data, follow=True)
		form = CreatePollForm(poll_data)
		self.assertFalse(form.is_valid())

	def test_create_question_one_choice(self):
		"""
		This test checks if a poll can be published with only one choice.
		"""
		user = User.objects.create_user(username='test',password='testpass')
		username='test'
		password='testpass'
		self.client.login(username=username,password=password)
		poll_data = {'poll_name': 'Poll Text', 'poll_pub_date': timezone.now(), 'poll_answer1':'Answer1', 'poll_answer2':'', 'poll_answer3':''}
		response = self.client.post(reverse("polls:createpoll"), poll_data, follow=True)
		form = CreatePollForm(poll_data)
		self.assertFalse(form.is_valid())

	def test_create_question_two_choices(self):
		"""
		This test checks if a poll can be published with two choices.
		"""
		user = User.objects.create_user(username='test',password='testpass')
		username='test'
		password='testpass'
		self.client.login(username=username,password=password)
		poll_data = {'poll_name': 'Poll Text', 'poll_pub_date': timezone.now(), 'poll_answer1':'Answer1', 'poll_answer2':'Answer2', 'poll_answer3':''}
		response = self.client.post(reverse("polls:createpoll"), poll_data, follow=True)
		form = CreatePollForm(poll_data)
		self.assertTrue(form.is_valid())

	def test_create_question_three_choices(self):
		"""
		This test checks if a poll can be published with all three choices.
		"""
		user = User.objects.create_user(username='test',password='testpass')
		username='test'
		password='testpass'
		self.client.login(username=username,password=password)
		poll_data = {'poll_name': 'Poll Text', 'poll_pub_date': timezone.now(), 'poll_answer1':'Answer1', 'poll_answer2':'Answer2', 'poll_answer3':'Answer3'}
		response = self.client.post(reverse("polls:createpoll"), poll_data, follow=True)
		form = CreatePollForm(poll_data)
		self.assertTrue(form.is_valid())