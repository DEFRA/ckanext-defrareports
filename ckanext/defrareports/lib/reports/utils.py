# coding=utf-8
import ckan.plugins.toolkit as toolkit
from ckanext.defrareports.helpers import slugify, unslugify
from ckanext.report.report_registry import REPORT_KEYS_OPTIONAL, REPORT_KEYS_REQUIRED
from ckan.logic import NotFound
from functools import wraps
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY


def _get_records(offset=0, org=None):
    query = ''
    if org is not None:
        query = 'organization:{}'.format(org)
    return toolkit.get_action('package_search')({}, {
        'q': query,
        'rows': 1000,
        'start': offset
    })


def get_all_datasets(org=None):
    """
    Return all datasets. Optionally restricted by org name.

    :param org: Restrict to given organisation
    :return: List of datasets
    """
    response = _get_records(0, org=org)
    total_records = response['count']
    datasets = response['results']
    while len(datasets) != total_records:
        response = _get_records(len(datasets), org=org)
        datasets += response['results']
    return datasets


def report(report_dict):
    context = {'ignore_auth': True}
    report_url = toolkit.url_for('report', report_name=report_dict['name'], qualified=True)
    site_title = toolkit.get_action('config_option_show')(context, {'key': 'ckan.site_title'})
    site_prefix = slugify(site_title)
    pretty_name = report_dict.get('title', unslugify(report_dict['name']))
    package_title = "{}: {}".format(site_title, pretty_name)
    package_name = "{}-{}".format(site_prefix, report_dict['name'])

    extra_info = {}
    for k in set(report_dict.keys()) - REPORT_KEYS_REQUIRED - REPORT_KEYS_OPTIONAL:
        extra_info[k] = report_dict[k]
        del report_dict[k]

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
            package.update(extra_info)
            save_action(context, package)
            return results

        report_dict['generate'] = save_report
        # Yes, we don't return a function here, meaning that the thing
        # we originally defined as a function is now in fact a dict.
        return report_dict
    return decorate


def generate_months(num=12):
    """
    Generate a list of months start from `num` months ago to the current month
    :param num: number of months to go back
    :return: List of date strings
    """
    prev = datetime.now() - relativedelta(months=num-1, day=1)
    return [x.strftime('%Y-%m-%d') for x in rrule(freq=MONTHLY, count=num, dtstart=prev)]
