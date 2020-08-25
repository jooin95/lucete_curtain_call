from django import forms


class FeedbackForm(forms.Form):
    fullName = forms.CharField(
        label=False, max_length=100, widget=forms.TextInput(attrs={
            'placeholder': 'Full name'}))
    email = forms.EmailField(label=False)
    feedback = forms.CharField(label=False, widget=forms.Textarea)
