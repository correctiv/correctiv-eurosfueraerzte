import smtplib

from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .base import PaymentRecipient, PharmaPayment
from ..apps import EFA_COUNTRIES


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

    def get_absolute_domain_url(self):
        return settings.SITE_URL + self.get_absolute_url()

    def get_submissions(self):
        if not hasattr(self, '_submissions'):
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

    def send_login_email(self):
        content = render_to_string('correctiv_eurosfueraerzte/zerodocs/email_link.txt', {
            'object': self
        })
        try:
            send_mail(_('Your Zero Euro Doctor Link'), content,
                'nulleuro@correctiv.org',
                [self.email],
                fail_silently=False)
        except smtplib.SMTPException:
            return False
        self.email_sent = timezone.now()
        self.save()
        return True


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
