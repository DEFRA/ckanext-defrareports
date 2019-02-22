"""Tests for plugin.py."""
from ckan.tests.helpers import mock_action
from base import BaseTest
from nose.tools import assert_equal
from ckanext.defrareports import helpers


class TestDefraReportHelpers(BaseTest):
    """
    Test the various report helpers
    """

    @mock_action('package_search')
    @mock_action('organization_list')
    @mock_action('harvest_source_list')
    def test_get_report_index(self, mock_package_search, mock_organization_list, mock_harvest_source_list):
        mock_package_search.return_value = {
            'count': 2,
            'results': [
                {"id": "xxx"},
                {"id": "yyy"},
            ]
        }
        mock_organization_list.return_value = [1, 2, 3]
        mock_harvest_source_list.return_value = [1, 2, 3, 4]

        assert_equal(
            helpers.get_report_index(),
            {
                'modified_packages': [{'id': 'xxx'}, {'id': 'yyy'}],
                'statistics': {
                    'organisation_count': 3,
                    'dataset_count': 2,
                    'harvester_count': 4,
                    'resource_count': 0
                },
                'new_packages': [{'id': 'xxx'}, {'id': 'yyy'}]
            }

        )

    def test_get_package_extras(self):
        package = {
            'extras': [{
                    "key": "contact-email",
                    "value": "test@test.com"
                }, {
                    "key": "temporal-extent-begin",
                    "value": "2013-01-02"
                }
            ],
        }
        assert_equal(
            helpers.get_package_extras(package),
            {
                'contact-email': 'test@test.com',
                'temporal-extent-begin': '2013-01-02'
            }
        )

    def test_slugify(self):
        assert_equal(
            helpers.slugify('This is a test'),
            'this-is-a-test'
        )

    def test_unslugify(self):
        assert_equal(
            helpers.unslugify('this-is-a-test'),
            'This is a test'
        )
