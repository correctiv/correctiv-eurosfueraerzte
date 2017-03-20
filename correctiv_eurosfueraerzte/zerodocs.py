# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT


def generate_pdf(f, obj):
    doc = SimpleDocTemplate(f, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))

    p = []
    data = {
        'title': obj.title,
        'first_name': obj.first_name,
        'last_name': obj.last_name,
        'address': obj.address,
        'postcode': obj.postcode,
        'location': obj.location,
        'country': obj.get_country_display(),
    }
    address = [
        '{title} {first_name} {last_name}',
        '{address}',
        '{postcode} {location}',
        '{country}'
    ]
    for a in address:
        p.append(Paragraph(a.format(**data), styles["Right"]))

    p.append(Spacer(1, 12 * 5))

    address = [
        'CORRECTIV - Recherchen für die Gesellschaft gGmbH',
        'Singerstr. 109',
        '10179 Berlin',
        'Deutschland',
    ]
    for a in address:
        p.append(Paragraph(a, styles["Normal"]))

    p.append(Spacer(1, 12))
    p.append(Paragraph('Fax: +49 (0) 30 – 555 780 2 20', styles['Normal']))

    p.append(Spacer(1, 12 * 4))

    now = timezone.now()
    p.append(Paragraph(now.strftime('%d.%m.%Y'), styles["Right"]))

    p.append(Paragraph('Bestätigung meines Eintrags in Ihrer Null-Euro-Ärzte-Datenbank', styles["Normal"]))

    p.append(Paragraph('Aktenzeichen: {date}-{pk}'.format(
        date=obj.last_login.strftime('%Y%m%d'),
        pk=obj.pk
    ), styles["Normal"]))

    # p.append(Paragraph('URL: <a href="{url}">{url}</a>'.format(
    #     url=obj.get_absolute_domain_url()
    # ), styles["Normal"]))

    p.append(Spacer(1, 12 * 3))

    years = [str(sub.date.year) for sub in obj.get_submissions()]
    if len(years) > 1:
        year_prefix = 'den Jahren'
        year_str = '{} und {}'.format(', '.join(years[:-1]), years[-1])
    else:
        year_prefix = 'im Jahr'
        year_str = years[0]

    text = [
        'Sehr geehrte Damen und Herren,',
        None,
        'hiermit bestätige ich, dass ich in {} {} keine Gelder '
        'oder geldwerte Leistungen von Unternehmen der Pharmaindustrie erhalten habe.'.format(year_prefix, year_str),
        None,
        'Ich stimme der Veröffentlichung meines vollständigen Namens, meiner beruflichen Adresse und der gemachten Angaben zu.',
        None,
        'Mit freundlichen Grüßen',
        None,
        None,
        None,
        None,
        '_' * 50,
        '(Unterschrift %s)' % obj.get_full_name(),
    ] + ([None] * 12) + [
        '_' * 50,
        '(Stempel %s)' % obj.get_full_name(),
    ]

    for t in text:
        if t is None:
            p.append(Spacer(1, 12))
        else:
            p.append(Paragraph(t, styles["Normal"]))

    doc.build(p)
