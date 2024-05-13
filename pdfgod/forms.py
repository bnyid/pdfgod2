from django import forms
from .models import Category, Section, Group, Folder, Pdf


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']




    