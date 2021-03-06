import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form
from django.utils.translation import ugettext_lazy as _

from users.models import Profile, User, Subscriptions, generate_avatar


def has_cyrillic(text):
    return bool(re.search('[\u0400-\u04FF]', text))


def only_cyrillic(text):
    return bool(re.fullmatch('[\u0400-\u04FF\-]*', text))


class PersonalForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name', 'first_name_rus', 'middle_name_rus',
            'last_name_rus', 'country', 'city', 'birthday', 'preferred_language'
        )
        widgets = {
            'birthday': forms.TextInput(attrs={'class': 'datepicker'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'e.g.: Ivan',
            'last_name': 'e.g.: Petrov',
            'first_name_rus': 'пр.: Иван',
            'middle_name_rus': 'пр.: Дмитриевич',
            'last_name_rus': 'пр.: Петров',
            'city': 'e.g.: Moscow',
            'birthday': 'e.g.: 1980-02-20',
        }
        for key, value in placeholders.items():
            self.fields[key].widget.attrs['placeholder'] = value

    def clean_first_name(self):
        if has_cyrillic(self.cleaned_data['first_name']):
            raise ValidationError(
                _('This field should be written in English'),
                code='invalid_language'
            )
        return self.cleaned_data['first_name']

    def clean_last_name(self):
        if has_cyrillic(self.cleaned_data['last_name']):
            raise ValidationError(
                _('This field should be written in English'),
                code='invalid_language'
            )
        return self.cleaned_data['last_name']

    def clean_city(self):
        if has_cyrillic(self.cleaned_data['city']):
            raise ValidationError(
                _('This field should be written in English'),
                code='invalid_language'
            )
        return self.cleaned_data['city']

    def clean_first_name_rus(self):
        if not only_cyrillic(self.cleaned_data['first_name_rus']):
            raise ValidationError(
                _('Field should contain only cyrillic characters'),
                code='invalid_language'
            )
        return self.cleaned_data['first_name_rus']

    def clean_middle_name_rus(self):
        if not only_cyrillic(self.cleaned_data['middle_name_rus']):
            raise ValidationError(
                _('Field should contain only cyrillic characters'),
                code='invalid_language'
            )
        return self.cleaned_data['middle_name_rus']

    def clean_last_name_rus(self):
        if not only_cyrillic(self.cleaned_data['last_name_rus']):
            raise ValidationError(
                _('Field should contain only cyrillic characters'),
                code='invalid_language'
            )
        return self.cleaned_data['last_name_rus']


class ProfessionalForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('affiliation', 'degree', 'role', 'ieee_member')

    def clean_affiliation(self):
        if has_cyrillic(self.cleaned_data['affiliation']):
            raise ValidationError(
                _('This field should be written in English'),
                code='invalid_language'
            )
        return self.cleaned_data['affiliation']


class SubscriptionsForm(forms.ModelForm):
    class Meta:
        model = Subscriptions
        fields = ('trans_email', 'info_email')


class PasswordProtectedForm(Form):
    password = forms.CharField(
        strip=False,
        label=_('Enter your password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Password')})
    )

    def clean_password(self):
        """Validate that the entered password is correct.
        """
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(
                _("The password is incorrect"),
                code='password_incorrect'
            )
        return password


class DeleteUserForm(PasswordProtectedForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self):
        self.user.delete()


class UpdateEmailForm(PasswordProtectedForm):
    email = forms.EmailField(label=_('Enter your new email'))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self):
        self.user.email = self.cleaned_data['email']
        self.user.save()


class DeleteAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ()

    def save(self, commit=True):
        if self.instance.avatar:
            self.instance.avatar.delete()
            self.instance.avatar_version += 1
            self.instance.avatar = generate_avatar(self.instance)
        return super().save(commit)
