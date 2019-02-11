import logging
from datetime import datetime, timedelta

import requests
from dateutil import parser
from requests import RequestException

from ckan.plugins import toolkit
from ckanext.defrareports.helpers import get_package_extras

logger = logging.getLogger('ckan')


def check_dataset_resources_job(dataset):
    """
    Background job to check whether resources for a dataset exist.
    """
    for resource in dataset['resources']:
        try:
            resp = requests.head(resource['url'], verify=False, timeout=10)
        except RequestException:
            status = 'invalid'
        else:
            if resp.status_code == 200:
                status = 'active'
            else:
                status = 'dead'

        if status != resource.get('link_status'):
            toolkit.get_action('resource_patch')({
                'ignore_auth': True
            }, {
                'id': resource['id'],
                'link_status': status,
                'link_status_last_check': datetime.now().isoformat()
            })


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

    def _needs_check(self, dataset):
        # Private resources don't need to be checked
        if get_package_extras(dataset).get('private-resources', False):
            return False

        # Resources need to be checked if they haven't been updated in the last 6 days
        for resource in dataset['resource']:
            # Only check the file if it hasn't been checked in the last week
            last_check = resource.get('link_status_last_check')
            cutoff = datetime.now() - timedelta(days=6)
            if last_check is None or parser.parse(last_check) < cutoff:
                return True
        return False

    def command(self):
        self._load_config()
        datasets = self._get_all_datasets()
        for dataset in datasets:
            if self._needs_check(dataset):
                toolkit.enqueue_job(
                    check_dataset_resources_job,
                    [dataset],
                    title='Resource check for {}'.format(dataset['name'])
                )
        logger.info('Enqueued resource check jobs for {} resources'.format(len(datasets)))
