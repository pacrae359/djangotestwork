from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
import datetime

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class CreatePollForm(forms.Form):
	poll_name = forms.CharField(
		label="Poll Text (256 Characters Max!)",
		max_length=256,
		required=True,
		widget=forms.Textarea(attrs={"rows":"5"})
		)
	poll_pub_date = forms.DateTimeField(
		label="Publish Date (Dates in the past will not be valid)",
		widget = forms.DateInput(
			format="%d/%m/%Y", 
			attrs={"type": "date"}),
			input_formats=["%d/%m/%Y"],
			required=True
		)
	poll_answer1 = forms.CharField(
		label="Answer Number 1",
		max_length=128,
		required=True,
		widget=forms.Textarea(attrs={"rows":"2"})
		)
	poll_answer2 = forms.CharField(
		label="Answer Number 2",
		max_length=128,
		required=True,
		widget=forms.Textarea(attrs={"rows":"2"})
		)
	poll_answer3 = forms.CharField(
		label="Answer Number 3 (Optional!)",
		max_length=128,
		required=False,
		widget=forms.Textarea(attrs={"rows":"2"})
		)
	
