from ckan.plugins.toolkit import _, request, get_action
import json


def get_report_index():
    import ckan.plugins.toolkit as toolkit
    from ckan import model

    context = {}

    # Retrieve a list of the 5 most recently modified packages
    results = {
        'modified_packages': toolkit.get_action('package_search')(
            context, {
                'q': '',
                'sort': 'metadata_modified desc',
                'rows': 5
            }
        )['results']
    }

    # Retrieve the 5 most recently added packages, but don't
    # yet make them available
    res = toolkit.get_action('package_search')(
        context, {
            'q': '',
            'sort': 'metadata_created desc',
            'rows': 5
        }
    )

    # Pluck the total number of datasets before we assign the
    # results from the previous call
    pkg_total = res['count']
    results['new_packages'] = res['results']

    # org count
    org_count = len(toolkit.get_action('organization_list')(context, {}))

    # Number of harvesters
    harvester_count = len(toolkit.get_action('harvest_source_list')(
        context, {}
    ))

    # Number of resources...
    resource_count = model.Session.query(model.Resource).filter(model.Resource.state == 'active')

    results['statistics'] = {
        'harvester_count': harvester_count,
        'dataset_count': pkg_total,
        'organisation_count': org_count,
        'resource_count': resource_count.count()
    }
    return results


def report_row(msg, row, key):
    dates = sorted(list(row))[0:12]
    res = [row[d][key] for d in dates]
    return [msg] + res


def copy_and_merge(num_cells, from_list, add_to):
    l = add_to[:]
    source = sorted(list(from_list))
    l.extend(source[0:num_cells])
    return json.dumps(l)


def get_package_extras(pkg):
    if pkg is None:
        return {}

    extras = pkg.get('extras', [])
    if isinstance(extras, dict):
        return extras

    response = {}
    for extra in extras:
        response[extra['key']] = extra['value']

    return response


def is_private_resource(pkg):
    return get_package_extras(pkg).get('private-resources') == "True"
