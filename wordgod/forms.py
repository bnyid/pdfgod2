from django import forms

class TextInputForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label='텍스트 입력')


class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='엑셀 파일 업로드')
    