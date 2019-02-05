# A prototype report for showing the quality of the metadata that we have
# retrieved.  Currently this just gives every dataset a score of 100 and
# then removes points for bad metadata.  At present we only have a couple
# of criteria, but we can always add others in the rank_dataset function.

import ckan.plugins.toolkit as toolkit
from ckanext.defrareports.lib.quality import score_record
from ckanext.defrareports.lib.reports.utils import report, get_all_datasets


def bad_record(dataset, reasons):
    return {
        'name': dataset['name'],
        'title': dataset['title'],
        'reasons': reasons
    }


@report({
    'name': 'quality',
    'title': 'Metadata quality',
    'option_defaults': {},
    'option_combinations': None,
    'owner_org': 'defra',
    'license_id': 'uk-ogl',
    'maintainer': 'Simon Worthington',
    'maintainer_email': 'simon.worthington@defra.gsi.gov.uk',
    'extras': [{'key': 'frequency-of-update', 'value': 'daily'}],
    'template': 'report/quality.html'
})
def quality_report():
    """The quality of the metadata collected for each organisation.
    The score is calculated according to adherence to the published
    Defra metadata standards.
    """
    # Report which measures the quality of metadata within a publisher
    table = []
    context = {}

    organisation_list = toolkit.get_action('organization_list')(
        context, {
            'all_fields': True,
            'include_datasets': True
        }
    )

    for organisation in organisation_list:
        entry = {
         'name': organisation['name'],
         'title': organisation['title'],
         'average': 0,
         'record_count': 0,
         'worst_offenders': []
        }

        datasets = get_all_datasets(org=organisation['name'])

        ranked = []
        for dataset in datasets:
            (score, reasons) = score_record(dataset)
            entry['record_count'] += 1
            entry['average'] += score

            ranked.append((score, bad_record(dataset, reasons)))

        if entry['record_count'] > 0:
            entry['average'] /= entry['record_count']

        ranked.sort(key=lambda t: t[0])
        bad_entries = [r for r in ranked if r[0] < 100][0:5]

        entry['worst_offenders'] = bad_entries
        table.append(entry)

    return {
        'table': table
    }
