import os

from django import forms
from django.core.mail import EmailMessage

class InquiryForm(forms.Form):
        name = forms.CharField(label='お名前', max_length=30)
        email = forms.EmailField(label='メールアドレス')
        title = forms.CharField(label='タイトル', max_length=30)
        message = forms.CharField(label='メッセージ', widget=forms.Textarea)

        def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.fields['name'].widget.attrs['class'] = 'form-control'
                self.fields['name'].widget.attrs['placeholder'] = 'お名前をここに入力してください'

                self.fields['email'].widget.attrs['class'] = 'form-control'
                self.fields['email'].widget.attrs['placeholder'] = 'メールアドレスをここに入力してください'

                self.fields['title'].widget.attrs['class'] = 'form-control'
                self.fields['title'].widget.attrs['placeholder'] = 'タイトルをここに入力してください'

                self.fields['message'].widget.attrs['class'] = 'form-control'
                self.fields['message'].widget.attrs['placeholder'] = 'メッセージをここに入力してください'

        def send_email(self):
                name = self.cleaned_data['name']
                email = self.cleaned_data['email']
                title = self.cleaned_data['title']
                message = self.cleaned_data['message']

                subject = 'お問い合わせ{}'.format(title)
                message = '送信者:{0}\nメールアドレス:{1}\nメッセージ:\n{2}'.format(name, email, message)
                form_email = os.environ.get('FROM_EMAIL')
                to_list = [
                        os.environ.get('FROM_EMAIL')
                ]
                cc_list = [
                        email
                ]

                message = EmailMessage(
                        subject=subject,
                        body=message,
                        from_email=form_email,
                        to=to_list,
                        cc=cc_list
                        )
                message.send()