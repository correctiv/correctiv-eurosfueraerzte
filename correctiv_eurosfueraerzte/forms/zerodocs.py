from datetime import datetime, timedelta

from django.contrib.gis import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.urlresolvers import reverse_lazy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset
from crispy_forms.bootstrap import StrictButton

from ..models.zerodocs import ZeroDoctor, ZeroDocSubmission
from ..apps import EFA_COUNTRIES_CHOICE, EFA_YEARS
from ..geocode import geocode


def generate_secret():
    CHARSET = 'abcdefhikmnpqrstuvwxyz234568'
    LENGTH = 8
    exists = True
    while exists:
        secret = get_random_string(length=LENGTH, allowed_chars=CHARSET)
        exists = ZeroDoctor.objects.filter(secret=secret).exists()
    return secret


class ZeroDocLoginForm(forms.ModelForm):
    # terms = forms.BooleanField(label=_('I agree to the publication of '
    #                     'my name, business address and statements.'),
    #         help_text=_('Your email address will not be published.'))

    class Meta:
        model = ZeroDoctor
        fields = ('gender', 'title', 'first_name', 'last_name', 'email',)
        help_texts = {
            'email': _('We will send you an email to confirm your address.'),
        }

    def __init__(self, *args, **kwargs):
        super(ZeroDocLoginForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('eurosfueraerzte:eurosfueraerzte'
                                               '-zerodocs_login')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        layout_elements = list(self.fields.keys())

        layout = layout_elements + [
            StrictButton(_(u'Create or change your entry'),
                css_class='btn-success btn-lg', type='submit')
        ]
        self.helper.layout = Layout(*layout)

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            zerodoc = ZeroDoctor.objects.get(email=email)
            now = timezone.now()
            if zerodoc.email_sent and (now - zerodoc.email_sent) < timedelta(hours=12):
                raise forms.ValidationError(_('Last login has been less than 12 hours ago. Please use the link in the email we sent you.'))
        except ZeroDoctor.DoesNotExist:
            pass
        return email.lower()

    def clean(self):
        # overwrite and intentionally not call validate_unique
        return self.cleaned_data

    def save(self):
        cd = dict(self.cleaned_data)
        email = cd.pop('email')
        cd['secret'] = generate_secret()
        zd, created = ZeroDoctor.objects.get_or_create(email=email, defaults=cd)
        return zd


class ZeroDocSubmitForm(forms.ModelForm):
    address = forms.CharField(label=_('address'))
    postcode = forms.CharField(label=_('postcode'))
    location = forms.CharField(label=_('location'))
    country = forms.ChoiceField(label=_('country'),
                                choices=EFA_COUNTRIES_CHOICE)

    years = forms.TypedMultipleChoiceField(
        label=_('Please check all years that apply:'),
        widget=forms.CheckboxSelectMultiple(),
        coerce=int,
        required=False
    )

    class Meta:
        model = ZeroDoctor
        fields = ('gender', 'title', 'first_name', 'last_name', 'address',
                  'postcode', 'location', 'country')

    def __init__(self, *args, **kwargs):
        super(ZeroDocSubmitForm, self).__init__(*args, **kwargs)
        confirmed_years = set(x.date.year for x in self.instance.get_submissions()
                           if x.confirmed)
        remaining_years = [y for y in EFA_YEARS if y not in confirmed_years]
        self.fields['years'].choices = [
            (y, _('In %d I have not received any money from pharmaceutical companies.') % y)
            for y in remaining_years
        ]
        self.fields['years'].initial = [x.date.year for x in self.instance.get_submissions()]
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        name_elements = ['gender', 'title', 'first_name', 'last_name']
        addr_elements = ['address', 'postcode', 'location', 'country']

        layout = [
            Fieldset(
                _('Your name'),
                *name_elements
            ),
            Fieldset(
                _('Your business address'),
                *addr_elements
            )]
        if remaining_years:
            layout += [Fieldset(
                _('You have not received money from the pharma industry in these years'),
                'years'
            )]
        layout += [
            StrictButton(_(u'Submit'),
                css_class='btn-success btn-lg', type='submit')
        ]
        self.helper.layout = Layout(*layout)

    def save(self):
        obj = super(ZeroDocSubmitForm, self).save(commit=False)

        point = geocode(obj)

        obj.geo = point
        obj.save()

        if obj.recipient is not None:
            obj.create_or_update_recipient()

        submitted_years = set(self.cleaned_data['years'])
        current_tz = timezone.get_current_timezone()
        for year in EFA_YEARS:
            date = current_tz.localize(datetime(year, 1, 1))
            if year in submitted_years:
                ZeroDocSubmission.objects.get_or_create(zerodoc=obj, date=date, defaults={
                    'submitted_on': timezone.now()
                })
            else:
                ZeroDocSubmission.objects.filter(
                    zerodoc=obj, date=date, confirmed=False
                ).delete()
        obj._submissions = None

        if submitted_years:
            obj.send_submission_email()

        return obj
