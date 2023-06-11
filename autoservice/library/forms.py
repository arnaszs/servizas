from django import forms
from . import models


class DateInput(forms.DateInput):
    input_type = 'date'


class OrderReviewForm(forms.ModelForm):
    class Meta:
        model = models.OrderReview
        fields = ('content', 'order', 'reviewer')
        widgets = {
            'order': forms.HiddenInput(),
            'reviewer': forms.HiddenInput(),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ('car', 'due_back')
        widgets = {
            'due_back': DateInput(),
        }
