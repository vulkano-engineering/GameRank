from django import forms
from .models import Vote, Follow, Comment

class VoteForm(forms.ModelForm):
    score = forms.IntegerField(
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={'type': 'range', 'step': '1'}),
        label="Your Score (0-5)"
    )

    class Meta:
        model = Vote
        fields = ['score']

class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = [] # No fields needed, just the button press

class CommentForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Your Comment"
    )

    class Meta:
        model = Comment
        fields = ['body'] 