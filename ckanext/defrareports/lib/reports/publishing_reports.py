from collections import defaultdict
from datetime import datetime

import ckan.plugins.toolkit as toolkit
from ckanext.defrareports.lib.reports.utils import report

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY


@report({
    'name': 'publishing',
    'title': 'Publishing',
    'option_defaults': {},
    'option_combinations': None,
    'owner_org': 'defra',
    'license_id': 'uk-ogl',
    'maintainer': 'Simon Worthington',
    'maintainer_email': 'simon.worthington@defra.gsi.gov.uk',
    'extras': [{'key': 'frequency-of-update', 'value': 'daily'}],
    'template': 'report/publishing.html'
})
def publishing_history_report():
    """For each organisation, this report shows both the addition on new dataset records and
    the modification of those records for the last 12 months."""
    table = []
    context = {}

    # Generate a list of dates for the last 12 months
    one_year_prev = datetime.now() - relativedelta(months=11, day=1)
    months = [x.strftime('%Y-%m-%d') for x in rrule(freq=MONTHLY, count=12, dtstart=one_year_prev)]
    organisation_list = toolkit.get_action('organization_list')(
        context, {
            'all_fields': True,
            'include_datasets': True
        }
    )

    for organisation in organisation_list:
        datasets = toolkit.get_action('package_search')(
            context, {
                'q': 'owner_org:{}'.format(organisation['id']),
                'rows': 10000
            }
        )['results']

        entry = {
            'name': organisation['name'],
            'title': organisation['title'],
        }

        def new_inner_dict():
            return {'added': 0, 'modified': 0}

        values = defaultdict(new_inner_dict)
        for dataset in datasets:
            date = datetime.strptime(dataset['metadata_created'], '%Y-%m-%dT%H:%M:%S.%f')
            created_date = date.strftime('%Y-%m-01')
            values[created_date]['added'] = values[created_date]['added'] + 1
            modified_date = datetime.strptime(dataset['metadata_modified'], '%Y-%m-%dT%H:%M:%S.%f')
            values[modified_date]['modified'] = values[modified_date]['modified'] + 1

        for month in months:
            entry[month] = values[month]

        table.append(entry)

    return {
        'table': table
    }
