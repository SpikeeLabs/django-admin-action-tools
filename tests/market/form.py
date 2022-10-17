from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime, AdminTextareaWidget


class NoteActionForm(forms.Form):
    date = forms.SplitDateTimeField(widget=AdminSplitDateTime(), help_text="datetime")
    note = forms.CharField(widget=AdminTextareaWidget(), help_text="note to add")


class NoteClearForm(forms.Form):
    clear_notes = forms.BooleanField()
