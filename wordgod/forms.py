from django import forms

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='엑셀 파일 업로드')
    
    