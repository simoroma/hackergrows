from django import forms

from .models import Comment, Story


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class AddStoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['original_url', 'product_url', 'text']

    def clean(self):
        cleaned_data = super().clean()

        text = self.cleaned_data.get('text')
        original_url = self.cleaned_data.get('original_url')
        product_url = self.cleaned_data.get('product_url')

        if not original_url:
            raise forms.ValidationError(
                "Please provide URL to relevant discussion.")

        if not product_url:
            raise forms.ValidationError(
                "Please provide URL to a product.")


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'text']
