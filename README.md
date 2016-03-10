# Euros für Ärzte (Euros for Doctors)

Django / Django CMS App powering our [“Euros für Ärzte” investigation](https://correctiv.org/recherchen/euros-fuer-aerzte/).

## Installation

Clone and install via

    pip install -e .

Add `correctiv_eurosfueraerzte` to your `INSTALLED_APPS`, then hook the
`urls.py` with a `'eurosfueraerzte'` namespace or add the CMS App into your CMS page tree.

Templates are made to work within our `correctiv.org` environment:

- a `CMS_TEMPLATE` variable is used as a base template location
- `django-sekizai` is used to add css / js
- a `number_utils` template tag is used

You might need to overwrite them, if you want to run this project in a different
environment.


## Configuration

`correctiv_eurosfueraerzte` requires a PostgreSQL database with Vector Field support.

Load in data and don't forget to run:

    ./manage.py update_search_field correctiv_eurosfueraerzte
