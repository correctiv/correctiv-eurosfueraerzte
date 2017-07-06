# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT


def get_year_formatter(years):
    if len(years) > 1:
        year_prefix = 'in den Jahren'
        year_str = '{} und {}'.format(', '.join(years[:-1]), years[-1])
    else:
        year_prefix = 'im Jahr'
        year_str = years[0]
    return year_prefix, year_str


SUBJECT = {
    'DE': 'Bestätigung meines Eintrags in Ihrer Null-Euro-Äzte-Datenbank',
    'CH': 'Bestätigung meines Eintrags in Ihrer Null-Franken-Ärzte-Datenbank'
}

ADDRESS = {
    'DE': [
        'CORRECTIV - Recherchen für die Gesellschaft gGmbH',
        'Singerstr. 109',
        '10179 Berlin',
        'Deutschland',
        None, None, None,
        'Fax: +49 (0) 30 – 555 780 2 20'
    ],
    'CH': [
        'Beobachter',
        'Ringier Axel Springer Schweiz AG',
        'z. Hd. Sylke Gruhnwald',
        'Flurstrasse 55',
        '8021 Zürich',
        None, None, None,
        'E-Mail: sylke.gruhnwald@beobachter.ch'
    ],
    'AT': [
        'CORRECTIV - Recherchen für die Gesellschaft gGmbH',
        'Singerstr. 109',
        '10179 Berlin',
        'Deutschland',
        None, None, None,
        'E-Mail: nulleuro@correctiv.org',
        None,
        'Fax: +49 (0) 30 – 555 780 2 20',
    ]
}

EFPIA_STATEMENT = {
    'DE': 'hiermit bestätige ich, dass ich {year_prefix} {year} keine Zuwendungen der Pharmaindustrie im Sinne des FSA/EFPIA-Kodex erhalten habe.',
    'CH': 'hiermit bestätige ich, dass ich {year_prefix} {year} keine Zuwendungen der Pharmaindustrie im Sinne des PKK/EFPIA-Kodex erhalten habe.',
}

NIS_NAME = {
    'DE': 'Anwendungsbeobachtungen/NIS',
    'CH': 'Praxiserfahrungsberichte'
}

CLOSING = {
    'DE': 'Mit freundlichen Grüßen',
    'CH': 'Mit freundlichen Grüssen'
}


def trans(dic, key, fallback='DE'):
    return dic.get(key, dic[fallback])


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
    doc_address = [
        '{title} {first_name} {last_name}',
        '{address}',
        '{postcode} {location}',
        '{country}'
    ]
    for a in doc_address:
        p.append(Paragraph(a.format(**data), styles["Right"]))

    p.append(Spacer(1, 12 * 5))

    for a in trans(ADDRESS, obj.country):
        if a is None:
            p.append(Spacer(1, 12))
        else:
            p.append(Paragraph(a, styles["Normal"]))

    p.append(Spacer(1, 12 * 4))

    now = timezone.now()
    p.append(Paragraph(now.strftime('%d.%m.%Y'), styles["Right"]))

    p.append(Paragraph(trans(SUBJECT, obj.country), styles["Normal"]))

    p.append(Paragraph('Aktenzeichen: {date}-{pk}'.format(
        date=obj.last_login.strftime('%Y%m%d'),
        pk=obj.pk
    ), styles["Normal"]))

    # p.append(Paragraph('URL: <a href="{url}">{url}</a>'.format(
    #     url=obj.get_absolute_domain_url()
    # ), styles["Normal"]))

    p.append(Spacer(1, 12 * 3))

    text = [
        'Sehr geehrte Damen und Herren,',
        None
    ]
    efpia_years = [str(sub.date.year) for sub in obj.get_efpia_submissions()]
    if efpia_years:
        year_prefix, year_str = get_year_formatter(efpia_years)
        text += [
            trans(EFPIA_STATEMENT,
                  obj.country).format(
                    year_prefix=year_prefix, year=year_str),
            None,
        ]
    obs_years = [str(sub.date.year) for sub in obj.get_observational_submissions()]
    if obs_years:
        year_prefix, year_str = get_year_formatter(obs_years)
        s = ('hiermit bestätige ich, dass ich {year_prefix} {year} keine Honorare '
             'für {obs} erhalten habe.')
        if efpia_years:
            s = ('Hiermit bestätige ich weiterhin, dass ich {year_prefix} {year} keine Honorare '
                 'für {obs} erhalten habe.')
        s = s.format(
            year_prefix=year_prefix,
            year=year_str,
            obs=trans(NIS_NAME, obj.country)
        )
        text += [
            s,
            None,
        ]

    text += [
        'Ich stimme der Veröffentlichung meines vollständigen Namens, meiner beruflichen Adresse und der oben gemachten Angaben zu.',
        None,
        trans(CLOSING, obj.country),
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
