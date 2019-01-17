# coding=utf-8
import re
import ckan.plugins.toolkit as toolkit
from ckan.logic import NotFound
from functools import partial

def _get_records(offset=0):
    return toolkit.get_action('package_search')({}, {
        'q': '',
        'rows': 1000,
        'start': offset
    })


def get_all_datasets():
    response = _get_records(0)
    total_records = response['count']
    datasets = response['results']
    while len(datasets) != total_records:
        response = _get_records(len(datasets))
        datasets += response['results']
    return datasets

def make_saveable_report(report_dict):
    report_dict['generate'] = partial(save_report, report_dict['generate'], report_dict)
    return report_dict

def save_report(generator, report_dict):
    context = {'ignore_auth': True}
    report_id = 'defra-report-{}'.format(report_dict['name'])
    report_url = toolkit.url_for('report', report_name=report_dict['name'], qualified=True)
    pretty_name = re.sub('[_-]', ' ', report_dict['name'].capitalize())
    try:
        toolkit.get_action('package_show')(context, {'name_or_id': report_id})
        save_action = toolkit.get_action('package_update')
    except NotFound:
        save_action = toolkit.get_action('package_create')

    results = generator()

    package = {
        'url': report_url,
        'name': report_id,
        'title': 'Defra Data Report: {}'.format(pretty_name),
        'notes': report_dict['description'],
        'private': False,
        'owner_org': 'defra',
        'resources': [{
            'url': report_url,
            'format': 'HTML',
            'mimetype': 'text/html',
            'name': '{} report'.format(pretty_name)
        },{
            'url': '{}?format=json'.format(report_url),
            'format': 'JSON',
            'mimetype': 'application/json',
            'name': '{} report – machine-readable data'.format(pretty_name)
        },{
            'url': '{}?format=csv'.format(report_url),
            'format': 'CSV',
            'mimetype': 'text/csv',
            'name': '{} report – tabular data'.format(pretty_name)
        }]
    }
    save_action(context, package)
    return results
