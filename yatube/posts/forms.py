from django import forms

from .models import Group, Post, Comment


class PostForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label='-Без группы-',
        required=False,
    )
    text = forms.CharField(
        widget=forms.Textarea,
        required=True,
    )

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
