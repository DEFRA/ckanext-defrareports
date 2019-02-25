from collections import defaultdict
from datetime import datetime

import ckan.plugins.toolkit as toolkit
from ckanext.defrareports.lib.reports.utils import report, generate_months, get_all_datasets


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
    data_table = []
    display_table = []
    context = {}

    organisation_list = toolkit.get_action('organization_list')(
        context, {
            'all_fields': True,
            'include_datasets': True
        }
    )

    for organisation in organisation_list:
        datasets = get_all_datasets(org=organisation['name'])

        display_entry = {
            'name': organisation['name'],
            'title': organisation['title'],
        }
        data_entry = {
            'Publisher': organisation['title']
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

        for month in generate_months():
            display_entry[month] = values[month]
            pretty_month = datetime.strptime(month, '%Y-%m-%d').strftime('%B %Y')
            data_entry['Added {}'.format(pretty_month)] = values[month]['added']
            data_entry['Modified {}'.format(pretty_month)] = values[month]['modified']

        display_table.append(display_entry)
        data_table.append(data_entry)

    return {
        'table': data_table,
        'display_table': display_table
    }
