# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.contrib.gis import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.html import format_html
from django.core.urlresolvers import reverse_lazy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset
from crispy_forms.bootstrap import StrictButton

from ..models.zerodocs import ZeroDoctor, ZeroDocSubmission
from ..apps import EFA_COUNTRIES_CHOICE, EFA_YEARS
from ..geocode import geocode


SUBMISSION_CHECKBOX_LABELS = (
    ('efpia', _('In %d I have not received any payments from pharmaceutical companies.')),
    ('observational', _('In %d I have not received fees for observational studies/NIS.'))
)


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

    years_efpia = forms.TypedMultipleChoiceField(
        label='',
        widget=forms.CheckboxSelectMultiple(),
        coerce=int,
        required=False,
        help_text=format_html(_('These are payments in accordance with the <a href="http://www.pharma-transparenz.de/ueber-den-transparenzkodex/die-eckpunkte-des-transparenzkodex/">transparency codex of the FSA.</a>'))
    )

    years_observational = forms.TypedMultipleChoiceField(
        label='',
        widget=forms.CheckboxSelectMultiple(),
        coerce=int,
        required=False
    )

    address_type = forms.ChoiceField(choices=(
        ('', '---'),
        ('Praxis', 'Praxis'),
        ('Klinik', 'Klinik'),
        ('MVZ', 'Medizinisches Versorgungszentrum'),
        ('Sonstiges', 'Sonstiges'),
    ), label=_('Type of address'))

    specialisation = forms.ChoiceField(label=_('your specialisation'),
            required=False, choices=(
        ('', '---'),
        ('Allgemeinmediziner', 'Allgemeinmediziner / Praktischer Arzt'),
        ('Internist', 'Facharzt für Innere Medizin / Internist'),
        ('Frauenheilkunde', 'Facharzt für Frauenheilkunde'),
        ('Kinderheilkunde', 'Facharzt für Kinderheilkunde'),
        ('Augenheilkunde', 'Facharzt für Augenheilkunde'),
        ('Hals-Nasen-Ohrenheilkunde', 'Facharzt für Hals-Nasen-Ohrenheilkunde'),
        ('Orthopädie', 'Facharzt für Orthopädie'),
        ('Chirurgie', 'Facharzt für Chirurgie'),
        ('Haut- und Geschlechtskrankheiten', 'Facharzt für Haut- und Geschlechtskrankheiten'),
        ('Radiologie und Nuklearmedizin', 'Facharzt für Radiologie und Nuklearmedizin'),
        ('Neurologie, Psychiatrie, Kinderpsychiatrie, Psychotherapie', 'Facharzt für Neurologie, Psychiatrie, Kinderpsychiatrie, Psychotherapie'),
        ('Urologie', 'Facharzt für Urologie'),
        ('Psychologischer Psychotherapeut', 'Psychologischer Psychotherapeut'),
        ('Zahnarzt', 'Zahnarzt'),
        ('Sonstige', 'Sonstige'),
    ))
    web = forms.URLField(label=_('website'), required=False,
                widget=forms.URLInput(attrs={'placeholder': 'http://'}))

    class Meta:
        model = ZeroDoctor
        fields = ('gender', 'title', 'first_name', 'last_name', 'address',
                  'postcode', 'location', 'country', 'specialisation', 'web')

    def __init__(self, *args, **kwargs):
        super(ZeroDocSubmitForm, self).__init__(*args, **kwargs)
        confirmed_years = {}
        remaining_years = {}
        year_field_names = []
        for kind, label in SUBMISSION_CHECKBOX_LABELS:
            confirmed_years[kind] = set(x.date.year for x in
                    self.instance.get_submissions(kind) if x.confirmed)
            remaining_years[kind] = [y for y in EFA_YEARS
                                     if y not in confirmed_years]

            year_field_name = 'years_%s' % kind
            self.fields[year_field_name].choices = [
                (y, label % y)
                for y in remaining_years[kind]
            ]
            self.fields[year_field_name].initial = [x.date.year for x in self.instance.get_submissions(kind)]
            year_field_names.append(year_field_name)

        any_remaining_years = any(x for x in remaining_years.values())
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        name_elements = ['gender', 'title', 'first_name', 'last_name']
        addr_elements = ['address_type', 'address', 'postcode', 'location',
                         'country']
        optional_elements = ['specialisation', 'web']

        layout = [
            Fieldset(
                _('Your name'),
                *name_elements
            ),
            Fieldset(
                _('Optional details'),
                *optional_elements
            ),
            Fieldset(
                _('Your business address'),
                *addr_elements
            ),
        ]
        if any_remaining_years:
            layout += [Fieldset(
                _('Please check all that apply:'),
                *year_field_names
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

        current_tz = timezone.get_current_timezone()
        has_submitted_years = False

        for kind, label in SUBMISSION_CHECKBOX_LABELS:
            submitted_years = set(self.cleaned_data['years_%s' % kind])
            if submitted_years:
                has_submitted_years = True

            for year in EFA_YEARS:
                date = current_tz.localize(datetime(year, 1, 1))
                if year in submitted_years:
                    ZeroDocSubmission.objects.get_or_create(
                        zerodoc=obj,
                        kind=kind,
                        date=date,
                        defaults={
                            'submitted_on': timezone.now()
                        }
                    )
                else:
                    ZeroDocSubmission.objects.filter(
                        zerodoc=obj, date=date, kind=kind, confirmed=False
                    ).delete()
        obj._submissions = None

        if has_submitted_years:
            obj.send_submission_email()

        return obj
