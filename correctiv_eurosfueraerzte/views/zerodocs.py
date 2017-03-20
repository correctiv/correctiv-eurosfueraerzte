'''

1. Give email address
2. Either find or create a ZeroDoctor with that address
3. Send a login link that also acts as email confirmation
4. Fill out rest of form, submit a confirmation that no money was received
5. (possibly find an existing doctor and match up)
6. Create 0-amount payment from no company

'''
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.utils import timezone

from ..forms.zerodocs import ZeroDocLoginForm, ZeroDocSubmitForm
from ..models.zerodocs import ZeroDoctor
from ..zerodocs import generate_pdf


class ZeroDocsIndexView(TemplateView):
    template_name = 'correctiv_eurosfueraerzte/zerodocs/index.html'

    def get_context_data(self):
        context = super(ZeroDocsIndexView, self).get_context_data()
        context['form'] = ZeroDocLoginForm()
        return context


def login(request):
    if request.method == 'POST':
        form = ZeroDocLoginForm(request.POST)
        if form.is_valid():
            zerodoc = form.save()
            result = zerodoc.send_login_email()
            if result:
                messages.add_message(request, messages.SUCCESS,
                    _('Please check your email!'))
                return redirect('eurosfueraerzte:eurosfueraerzte-zerodocs_email_sent')
            else:
                messages.add_message(request, messages.ERROR,
                    _('Email could not be sent, please check if it is correct!'))
        else:
            messages.add_message(request, messages.ERROR,
                _('Please check your form input again!'))
    else:
        form = ZeroDocLoginForm()
    return render(request, ZeroDocsIndexView.template_name, {
        'form': form
    })


class ZeroDocsEntryView(UpdateView):
    model = ZeroDoctor
    slug_field = 'secret'
    form_class = ZeroDocSubmitForm
    template_name = 'correctiv_eurosfueraerzte/zerodocs/form.html'

    def render_to_response(self, context, **response_kwargs):
        ZeroDoctor.objects.filter(pk=self.object.pk).update(
            last_login=timezone.now())
        return super(ZeroDocsEntryView, self).render_to_response(
            context, **response_kwargs
        )


def get_zerodocs_pdf(request, slug=None):
    obj = get_object_or_404(ZeroDoctor, secret=slug)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(
            # Translators: filename part
            _('letter_zeroeurodocs'))

    generate_pdf(response, obj)

    return response
