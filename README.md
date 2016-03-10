# Euros für Ärzte (Euros for Doctors)

Django / Django CMS App powering our [“Euros für Ärzte” investigation](https://correctiv.org/recherchen/euros-fuer-aerzte/).

## Installation

Add `correctiv_eurosfueraerzte` to your `INSTALLED_APPS`, then add the CMS App
into your CMS page tree.

## Configuration

Load in data and don't forget to run:

    ./manage.py update_search_field correctiv_eurosfueraerzte
