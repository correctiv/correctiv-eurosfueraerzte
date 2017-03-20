from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

import geocoder


SEARCH_URL = u'https://search.mapzen.com/v1/search'


def geocode_google(search, country):
    if not getattr(settings, 'GOOGLE_GEOCODE_APIKEY', None):
        return
    kwargs = {
        'key': settings.GOOGLE_GEOCODE_APIKEY,
        'language': country.lower(),
        'components': 'country:%s' % country,
    }

    geocoding_result = geocoder.google(search, **kwargs)
    latlng = None
    if geocoding_result.geojson['properties']['status'] == "OVER_QUERY_LIMIT":
        raise Exception('Over query API limit')
    if geocoding_result and geocoding_result.latlng:
        latlng = geocoding_result.latlng
    return latlng


def geocode(obj):
    q = ', '.join(x for x in (obj.address, obj.location) if x)
    latlng = geocode_google(q, obj.country)
    if latlng is None:
        return None
    point = GEOSGeometry('POINT(%f %f)' % (latlng[1], latlng[0]), srid=4326)
    return point
