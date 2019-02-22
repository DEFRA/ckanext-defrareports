import re

import sqlalchemy

import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckanext.defrareports.lib.reports.utils import report, generate_months
from ckanext.ga_report import ga_model
from ckanext.ga_report.ga_model import GA_Url


@report({
    'name': 'access',
    'title': 'Access metrics',
    'option_defaults': {},
    'option_combinations': None,
    'owner_org': 'defra',
    'license_id': 'uk-ogl',
    'maintainer': 'Simon Worthington',
    'maintainer_email': 'simon.worthington@defra.gsi.gov.uk',
    'extras': [{'key': 'frequency-of-update', 'value': 'daily'}],
    'template': 'report/access.html'
})
def access_history_report():
    """
    This reports shows how many times dataset pages have been accessed for each organisation.
    """
    display_table = []
    data_table = []
    context = {}

    organisation_list = toolkit.get_action('organization_list')(
        context, {
            'all_fields': True,
            'include_datasets': True
        }
    )

    org_ids = [x['name'] for x in organisation_list]

    # Get counts of visits per month per organisation from google analytics
    q = model.Session.query(
        GA_Url.department_id,
        GA_Url.period_name,
        sqlalchemy.func.sum(
            sqlalchemy.cast(GA_Url.pageviews, sqlalchemy.types.INT))
        ).filter(
            GA_Url.department_id.in_(org_ids)
        ).filter(
            GA_Url.url.like('/dataset/%')
        ).filter(
            GA_Url.package_id != ''
        ).filter(
            ga_model.GA_Url.period_name != 'All'
        ).group_by(GA_Url.department_id, GA_Url.period_name)

    # Build a mapping of org name to months
    stats = {x: {} for x in org_ids}
    months = generate_months()
    for org in stats.keys():
        stats[org] = {month: 0 for month in months}

    # Update org -> month map with any actual values gathered from GA
    for record in q.all():
        org_id, period, count = record
        full_month = '{}-01'.format(period)
        if full_month in stats[org_id]:
            stats[org_id][full_month] = int(count)

    # Build the graph entries for the template
    for org in organisation_list:
        display_entry = {
            'name': org['name'],
            'title': org['title'],
        }
        display_entry.update({month: {'visited': count} for month, count in stats[org['name']].iteritems()})
        display_table.append(display_entry)

        data_entry = {
            'Publisher': org['name']
        }
        data_entry.update({month: count for month, count in stats[org['name']].iteritems()})
        data_table.append(data_entry)

    return {
        'display_table': display_table,
        'table': data_table
    }
