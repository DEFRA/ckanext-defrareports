# A prototype report for showing the quality of the metadata that we have
# retrieved.  Currently this just gives every dataset a score of 100 and
# then removes points for bad metadata.  At present we only have a couple
# of criteria, but we can always add others in the rank_dataset function.
import ckan.plugins.toolkit as toolkit

from ckanext.defrareports.helpers import is_private_resource
from ckanext.defrareports.lib.reports.utils import get_all_datasets, report

@report({
    'name': 'system-stats',
    'title': 'System stats',
    'option_defaults': {},
    'option_combinations': None,
    'owner_org': 'defra',
    'license_id': 'uk-ogl',
    'maintainer': 'Simon Worthington',
    'maintainer_email': 'simon.worthington@defra.gsi.gov.uk',
    'extras': [{'key': 'frequency-of-update', 'value': 'daily'}],
    'template': 'report/system_stats.html'
})
def system_stats_report():
    'A compilation of the stats asked for in the planning meeting on Thu, 20 Dec 2018'
    # PROTOTYPE report that measures specific stats to allow us to make
    # decisions on the direction of the alpha
    counts = {
        'total_datasets': 0,
        'with_contact_email': 0,
        'with_maintainer_email': 0,
        'with_maintainer_name': 0,
        'licenses': {},
        'import_sources': {},
        'open_datasets': 0,
        'private_resources': 0,
        'resource_formats': {},
        'temporal_datasets': 0,
        'geospatial_datasets': 0,
    }

    harvest_sources = toolkit.get_action('harvest_source_list')({}, {
        'all': True
    })

    for dataset in get_all_datasets():
        extras = {extra['key']: extra['value'] for extra in dataset['extras']}

        if extras.get('contact-email', None) not in [None, '']:
            counts['with_contact_email'] += 1

        if dataset.get('maintainer_email', None) not in [None, '']:
            counts['with_maintainer_email'] += 1

        if dataset.get('maintainer', None) not in [None, '']:
            counts['with_maintainer_name'] += 1

        license = dataset.get('license_id', '')
        if license is None:
            license = ''

        if license not in counts['licenses']:
            counts['licenses'][license] = 0
        counts['licenses'][license] += 1

        source = extras.get('import_source', '')
        if source.startswith('ONS'):
            source = 'ONS Test Data'
        elif source == '':
            source = 'Unknown'
        if source not in counts['import_sources']:
            counts['import_sources'][source] = 0
        counts['import_sources'][source] += 1

        if dataset.get('is_open', False):
            counts['open_datasets'] += 1

        if is_private_resource(dataset):
            counts['private_resources'] += 1

        if extras.get('temporal-extent-begin') is not None and extras.get('temporal-extent-end') is not None:
            counts['temporal_datasets'] += 1

        if extras.get('spatial') is not None:
            counts['geospatial_datasets'] += 1

        for resource in dataset['resources']:
            if resource['format'] not in counts['resource_formats']:
                counts['resource_formats'][resource['format']] = 0
            counts['resource_formats'][resource['format']] += 1

        counts['total_datasets'] += 1

    return {
        'table': [{
            'Total Datasets': counts['total_datasets'],
            'Datasets with Contact Info': counts['with_contact_email'],
            'Datasets with Maintainer Email': counts['with_maintainer_email'],
            'Datasets with Maintainer Name': counts['with_maintainer_name'],
            'Open Datasets': counts['open_datasets'],
            'Private Resources': counts['private_resources'],
            'Datasets with Temporal Data': counts['temporal_datasets'],
            'Datasets with Geospatial Data': counts['geospatial_datasets'],
        }],
        'are_some_results': True,
        'counts': counts,
        'harvest_sources': harvest_sources,
    }
