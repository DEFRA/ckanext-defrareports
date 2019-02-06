import logging
import requests
from requests import RequestException

from ckan.logic import NotFound
from ckan.plugins import toolkit
from ckanext.defrareports.helpers import get_package_extras

logger = logging.getLogger('ckan')


def check_dataset_resources_job(dataset):
    """
    Background job to check whether resources for a dataset exist.
    """
    extras = get_package_extras(dataset)
    if extras.get('private-resources', False):
        return

    for resource in dataset['resources']:
        try:
            resp = requests.get(resource['url'])
        except RequestException:
            new_status = 'invalid'
        else:
            if resp.status_code == 200:
                new_status = 'active'
            else:
                new_status = 'dead'

        if new_status != resource.get('link_status'):
            try:
                toolkit.get_action('resource_patch')({
                    'ignore_auth': True
                }, {
                    'id': resource['id'],
                    'link_status': new_status
                })
            except NotFound:
                logger.warn('Resource {}, from Dataset {} not found'.format(
                    resource['id'], dataset['name'])
                )
            else:
                logger.info('Resource {}, from Dataset {} updated successfully'.format(
                    resource['id'], dataset['name'])
                )


class CheckBrokenResourcesCommand(toolkit.CkanCommand):
    """
    This command will check the url for every resource on the system.

    It will then set the link_status field to one of the following:
        * active - URL is accessible
        * dead - URL is inaccessible
        * invalid  - URL is invalid
    """
    summary = __doc__.split('\n')[0]

    @staticmethod
    def _get_records(offset=0):
        return toolkit.get_action('package_search')({
            'ignore_auth': True,
        }, {
            'q': '',
            'rows': 1000,
            'start': offset
        })

    def _get_all_datasets(self):
        """
        Return all datasets. Optionally restricted by org name.

        :param org: Restrict to given organisation
        :return: List of datasets
        """
        response = self._get_records(0)
        total_records = response['count']
        datasets = response['results']
        while len(datasets) != total_records:
            response = self._get_records(len(datasets))
            datasets += response['results']
        return datasets

    def _is_broken(self):
        pass

    def command(self):
        self._load_config()
        datasets = self._get_all_datasets()
        for dataset in datasets:
            toolkit.enqueue_job(
                check_dataset_resources_job,
                [dataset],
                title='Resource check for {}'.format(dataset['name'])
            )
        logger.info('Enqueued resource check jobs for {} resources'.format(len(datasets)))
