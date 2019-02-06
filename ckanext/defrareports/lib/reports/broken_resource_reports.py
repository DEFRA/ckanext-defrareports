import ckan.plugins.toolkit as toolkit
from ckanext.defrareports.lib.reports.utils import report, get_all_datasets


@report({
    'name': 'broken',
    'title': 'Broken records',
    'option_defaults': {},
    'option_combinations': None,
    'owner_org': 'defra',
    'license_id': 'uk-ogl',
    'maintainer': 'Simon Worthington',
    'maintainer_email': 'simon.worthington@defra.gsi.gov.uk',
    'extras': [{'key': 'frequency-of-update', 'value': 'daily'}],
    'template': 'report/broken.html'
})
def broken_resource_report():
    """The percentage of broken records, per organisation. A broken record is a link to
    a data resource which no longer works. This often happens when sites are redesigned
    but the metadata record is not updated."""
    table = []
    context = {}
    organisation_list = toolkit.get_action('organization_list')(
        context, {
            'all_fields': True,
            'include_datasets': True
        }
    )

    for organisation in organisation_list:
        datasets = get_all_datasets(org=organisation['name'])
        entry = {
            'name': organisation['name'],
            'title': organisation['title'],
            'total_datasets': len(datasets),
            'total_resources': 0,
            'broken_datasets': 0,
            'broken_resources': 0,
        }
        for dataset in datasets:
            broken = False
            for resource in dataset['resources']:
                entry['total_resources'] += 1
                if resource.get('link_status') != 'active':
                    entry['broken_resources'] += 1
                    broken = True
            if broken:
                entry['broken_datasets'] += 1

        table.append(entry)

    return {'table': table}
