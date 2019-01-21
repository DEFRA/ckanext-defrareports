# coding=utf-8
import re
import ckan.plugins.toolkit as toolkit
from ckanext.report.report_registry import REPORT_KEYS_OPTIONAL, REPORT_KEYS_REQUIRED
from ckan.logic import NotFound
from functools import wraps
from datetime import datetime

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

def report(report_dict):
    context = {'ignore_auth': True}
    report_url = toolkit.url_for('report', report_name=report_dict['name'], qualified=True)
    site_title = toolkit.get_action('config_option_show')(context, {'key': 'ckan.site_title'})
    site_prefix = re.sub('[^a-z0-9_-]', '-', site_title.lower())
    pretty_name = report_dict.get('title', re.sub('[_-]', ' ', report_dict['name'].capitalize()))
    package_title = "{}: {}".format(site_title, pretty_name)
    package_name = "{}-{}".format(site_prefix, report_dict['name'])
    owner_org = report_dict['owner_org']
    license = report_dict.get('license', None)

    def decorate(generator):
        if 'description' not in report_dict:
            report_dict['description'] = generator.__doc__

        @wraps(generator)
        def save_report(*args, **kwargs):
            results = generator(*args, **kwargs)

            try:
                toolkit.get_action('package_show')({'ignore_auth': True}, {'name_or_id': package_name})
                save_action = toolkit.get_action('package_update')
            except NotFound:
                save_action = toolkit.get_action('package_create')
            package = {
                'url': report_url,
                'name': package_name,
                'title': package_title,
                'notes': report_dict['description'],
                'private': False,
                'license_id': license,
                'owner_org': owner_org,
                'resources': [{
                    'url': report_url,
                    'format': 'HTML',
                    'mimetype': 'text/html',
                    'last_modified': datetime.now(),
                    'name': '{} report'.format(pretty_name)
                },{
                    'url': '{}?format=json'.format(report_url),
                    'format': 'JSON',
                    'mimetype': 'application/json',
                    'last_modified': datetime.now(),
                    'name': '{} report – machine-readable data'.format(pretty_name)
                },{
                    'url': '{}?format=csv'.format(report_url),
                    'format': 'CSV',
                    'mimetype': 'text/csv',
                    'last_modified': datetime.now(),
                    'name': '{} report – tabular data'.format(pretty_name)
                }]
            }
            save_action(context, package)
            return results

        report_dict['generate'] = save_report
        for unknown_key in set(report_dict.keys()) - REPORT_KEYS_REQUIRED - REPORT_KEYS_OPTIONAL:
            del report_dict[unknown_key]

        # Yes, we don't return a function here, meaning that the thing
        # we originally defined as a function is now in fact a dict.
        return report_dict
    return decorate