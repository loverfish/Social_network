from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Изображение',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
            }),
            'group': forms.Select(attrs={
                'class': 'form-select',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                # 'type': 'file',
            })
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий'}
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }
