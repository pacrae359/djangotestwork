from django.shortcuts import render, get_object_or_404, redirect

from django.db.models import F

from django.http import HttpResponseRedirect

from django.urls import reverse, reverse_lazy

from .models import Question, Choice

from .forms import CreateUserForm

from django.views import generic

from django.utils import timezone

from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

import logging

logger = logging.getLogger(__name__)
 
class IndexView(generic.ListView):
	template_name = "polls/index.html"
	context_object_name = "latest_question_list"
	def get_queryset(self):
		if self.request.user.is_superuser:
			return Question.objects.exclude(choice__question_id__isnull = True).order_by("-pub_date")[:5]
		else:
			return Question.objects.filter(pub_date__lte=timezone.now()).exclude(choice__question_id__isnull = True).order_by("-pub_date")[:5]
		
class DetailView(generic.DetailView):
	model = Question
	template_name = "polls/detail.html"

	def get_queryset(self):
		"""
		Excludes any questions with publish dates in the future.
		"""
		if self.request.user.is_superuser:
			return Question.objects.exclude(choice__question_id__isnull = True)
		else:
			return Question.objects.filter(pub_date__lte=timezone.now()).exclude(choice__question_id__isnull = True)

class ResultsView(generic.DetailView):
	model = Question
	template_name = "polls/results.html"

	def get_queryset(self):
		"""
		Exclude any questions with publish dates in the future, or ones that don't have any choices
		"""
		if self.request.user.is_superuser:
			return Question.objects.exclude(choice__question_id__isnull = True)
		else:
			return Question.objects.filter(pub_date__lte=timezone.now()).exclude(choice__question_id__isnull = True)

def loginPage(request):
	if not request.user.is_authenticated:
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('polls:index')
			else:
				messages.info(request, 'This Username and Password combination is not recognised. Please Try Again!')

		context = {}
		return render(request, 'polls/login.html', context)
	else:
		return redirect('polls:index')

def registerPage(request):
	form = CreateUserForm()

	if request.method == "POST":
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			user = form.cleaned_data.get('username')
			messages.success(request, "Account created for " + user)
			return redirect('polls:login')

	context = {"form": form}
	return render(request, 'polls/register.html', context)

def vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = question.choice_set.get(pk=request.POST["choice"])
	except (KeyError, Choice.DoesNotExist):
		return render(
			request,
			"polls/detail.html",
			{
				"question": question,
				"error_message": "You didn't select a choice.",
			},
		)
	else:
		# F() is used to avoid a race condition so multiple users can update values at
		# the same time and the correct value will be stored.
		selected_choice.votes = F("votes") + 1
		selected_choice.save()
		return HttpResponseRedirect(reverse("polls:results",args=(question.id,)))