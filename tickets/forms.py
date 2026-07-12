from django import forms
from .models import Ticket, Comment

class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket

        fields = [
            'title',
            'description',
            'category',
            'priority',
            "attachment",
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["message"]

        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write a reply..."
                }
            )
        }