import decimal
from io import BytesIO
import smtplib

from django.contrib.gis.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from slugify import slugify

from .base import PaymentRecipient, PharmaPayment
from ..apps import EFA_COUNTRIES
from ..zerodocs import generate_pdf


DEFAULT_FROM_EMAIL = 'nulleuro@correctiv.org'
# Translators: filename part
LETTER_FILENAME = _('letter_zeroeurodocs')

GENDER_CHOICES = (
    ('female', _('Ms.')),
    ('male', _('Mr.')),
)


@python_2_unicode_compatible
class ZeroDoctor(models.Model):
    gender = models.CharField(_('Mr/Ms'), max_length=20, choices=GENDER_CHOICES)
    title = models.CharField(_('title'), max_length=255, blank=True)

    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)

    email = models.EmailField(_('email address'), unique=True)
    email_sent = models.DateTimeField(null=True, blank=True)
    secret = models.SlugField(max_length=20)
    last_login = models.DateTimeField(null=True, blank=True)

    recipient = models.OneToOneField(PaymentRecipient, null=True, blank=True)

    address = models.CharField(_('address'), max_length=512, blank=True)
    postcode = models.CharField(_('postcode'), max_length=10, blank=True)
    location = models.CharField(_('location'), max_length=255, blank=True)
    country = models.CharField(_('country'), max_length=255, blank=True,
                               choices=EFA_COUNTRIES)

    geo = models.PointField(_('Geographic location'), geography=True,
                            blank=True, null=True)

    class Meta:
        verbose_name = _('Zero Doctor')
        verbose_name_plural = _('Zero Doctors')
        ordering = ('email_sent',)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    @models.permalink
    def get_absolute_url(self):
        return ('eurosfueraerzte:eurosfueraerzte-zerodocs_entry', (),
                {'slug': self.secret})

    @models.permalink
    def get_absolute_pdf_url(self):
        return ('eurosfueraerzte:eurosfueraerzte-zerodocs_pdf', (),
                {'slug': self.secret})

    def get_absolute_domain_url(self):
        return settings.SITE_URL + self.get_absolute_url()

    def get_absolute_domain_pdf_url(self):
        return settings.SITE_URL + self.get_absolute_pdf_url()

    def get_submissions(self):
        if not hasattr(self, '_submissions') or self._submissions is None:
            self._submissions = self.zerodocsubmission_set.all()
        return self._submissions

    def has_unconfirmed_submissions(self):
        return any(not x.confirmed for x in self.get_submissions())

    def get_gender_title(self):
        if self.title:
            return self.title
        return self.get_gender_display()

    def get_full_name(self):
        return u'{gender_title} {first_name} {last_name}'.format(
            gender_title=self.get_gender_title(),
            first_name=self.first_name,
            last_name=self.last_name,
        )

    def confirm_submissions(self, years):
        if not years:
            return

        years = set(years)

        # Create recipient
        if not self.recipient_id:
            self.create_or_update_recipient()

        for sub in self.get_submissions():
            if sub.date.year in years and not sub.confirmed:
                sub.confirmed = True
                sub.confirmed_on = timezone.now()
                sub.create_payment()

        self._submissions = None
        self.send_confirmed_email()

    def send_login_email(self):
        content = render_to_string('correctiv_eurosfueraerzte/zerodocs/email_link.txt', {
            'object': self
        })
        try:
            send_mail(_('Your Zero Euro Doctor Link'), content,
                DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=False)
        except smtplib.SMTPException:
            return False
        self.email_sent = timezone.now()
        self.save()
        return True

    def send_submission_email(self):
        content = render_to_string('correctiv_eurosfueraerzte/zerodocs/email_submitted.txt', {
            'object': self
        })
        email = EmailMessage(
            _('Your Zero Euro Doctor Submission'),
            content,
            DEFAULT_FROM_EMAIL,
            [self.email]
        )
        buffer = BytesIO()
        generate_pdf(buffer, self)
        email.attach('%s.pdf' % LETTER_FILENAME, buffer.getvalue(),
                     'application/pdf')
        try:
            email.send(fail_silently=False)
        except smtplib.SMTPException:
            return False
        return True

    def send_confirmed_email(self):
        content = render_to_string('correctiv_eurosfueraerzte/zerodocs/email_confirmed.txt', {
            'object': self,
            'url': self.recipient.get_absolute_domain_url()
        })
        email = EmailMessage(
            _('Your Zero Euro Doctor submission is confirmed'),
            content,
            DEFAULT_FROM_EMAIL,
            [self.email]
        )
        try:
            email.send(fail_silently=False)
        except smtplib.SMTPException:
            return False
        return True

    def create_or_update_recipient(self):
        kwargs = {
            'name': self.last_name,
            'slug': slugify('{first}-{last}-{location}-{country}'.format(
                first=self.first_name,
                last=self.last_name,
                location=self.location,
                country=self.country
            )),
            'origin': self.country,
            'kind': 0,
            'address': self.address,
            'postcode': self.postcode,
            'location': self.location,
            'country': self.country,
            'geo': self.geo,
            'first_name': self.first_name,
            'title': self.title,
            'gender': self.gender,
            'is_zerodoc': True
        }
        if self.recipient is None:
            if PaymentRecipient.objects.filter(slug=kwargs['slug']).exists():
                raise ValueError('Recipient with slug already exists')
            pr = PaymentRecipient.objects.create(**kwargs)
            PaymentRecipient.objects.filter(pk=pr.pk).update(
                    search_vector=PaymentRecipient.objects.get_search_vector())
            self.recipient = pr
            self.save()
        else:
            PaymentRecipient.objects.filter(pk=self.recipient_id).update(
                **kwargs
            )


class ZeroDocSubmission(models.Model):
    zerodoc = models.ForeignKey(ZeroDoctor)
    date = models.DateField()
    submitted_on = models.DateTimeField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    confirmed_on = models.DateTimeField(null=True, blank=True)

    payment = models.OneToOneField(PharmaPayment, null=True, blank=True)

    class Meta:
        verbose_name = _('Zero Doctor Submission')
        verbose_name_plural = _('Zero Doctors')
        ordering = ('date',)

    def __str__(self):
        return '%s -> %s' % (self.date.year, self.confirmed)

    def create_payment(self):
        if self.payment is not None:
            return
        kwargs = {
            'recipient': self.zerodoc.recipient,
            'date': self.date,
            'origin': self.zerodoc.country,
            'amount': decimal.Decimal(0.0),
            'amount_euro': decimal.Decimal(0.0),
        }
        pp = PharmaPayment.objects.create(**kwargs)
        self.payment = pp
        self.save()
