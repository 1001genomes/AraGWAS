"""
Functions to generate the schema for datacite
"""
#from django.template import Template
from django.template.loader import render_to_string
from django.conf import settings
from gwasdb.models import Study
import requests

def generate_schema(obj):
    """
    Creates XML schema for submitting a study to datacite
    """
    if isinstance(obj, Study):
        entity = 'study'
    else:
        raise ValueError('Entity %s not supported' % obj)
    context = {entity:obj}
    return render_to_string('%s_template.xml' % entity, context)



def submit_to_datacite(obj):
    """
    Register a Study or Phenotype with datacite
    """
    auth = (settings.DATACITE_USERNAME, settings.DATACITE_PASSWORD)
    url = settings.DOI_BASE_URL + obj.get_absolute_url()
    data = 'doi=%s\nurl=%s' % (obj.doi, url)
    metadata = generate_schema(obj)

    # if successful send metadata
    response = requests.post('%s/metadata' % settings.DATACITE_REST_URL,
                             auth=auth, data=metadata.encode('utf-8'),
                             headers={'Content-Type':'application/xml;charset=UTF-8'})
    if response.status_code != 201:
        raise Exception('Submitting metadata failed %s' % response.text)


    # send first doi request
    response = requests.post('%s/doi' % settings.DATACITE_REST_URL,
                             auth=auth, data=data,
                             headers={'Content-Type':'text/plain;charset=UTF-8'})

    if response.status_code != 201:
        raise Exception('Creating DOI failed: %s' % response.text)

    return response.text

def remove_from_datacite(obj):
    """
    Remove a GWAS Study from datacite
    """
    auth = (settings.DATACITE_USERNAME, settings.DATACITE_PASSWORD)
    url = settings.DOI_BASE_URL + obj.get_absolute_url()

    # if successful send metadata
    response = requests.delete('%s/metadata/%s' % (settings.DATACITE_REST_URL,obj.doi),
                             auth=auth,
                             headers={'Content-Type':'application/xml;charset=UTF-8'})
    if response.status_code != 200:
        raise Exception('Making dataset inactive failed %s' % response.text)
