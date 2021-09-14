from django import forms
from .models import *

forms.DateInput.input_type = 'date'


class CommentForm(forms.ModelForm):

    class Meta:
        
        model = Comment
        fields = ('author', 'text', )
    
    author = forms.CharField(widget=forms.TextInput, max_length=64, required=True)
    text = forms.CharField(widget=forms.Textarea, required=True)
    
    FIELDS_ATTRIBUTE_ID = {
        'author': 'comment-author',
        'text': 'comment-text',
    }
    
    FIELDS_ATTRIBUTE_CLASS = {
        'author': 'w-100 advanced-right',
        'text': 'w-100 advanced-right',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_attributes = dict()
            field_attributes['class'] = self.FIELDS_ATTRIBUTE_CLASS[field]
            field_attributes['id'] = self.FIELDS_ATTRIBUTE_ID[field]
            if field == 'author':
                field_attributes['value'] = kwargs.get('author')
            if field == 'text':
                self.fields[field].widget.attrs.pop('cols', None)
                self.fields[field].widget.attrs.pop('rows', None)
            self.fields[field].widget.attrs.update(field_attributes)
            