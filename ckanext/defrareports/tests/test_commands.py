"""Tests for plugin.py."""
import mock
from ckan.tests.helpers import mock_action
from requests import RequestException

from base import BaseTestCase
from nose.tools import assert_equal, assert_in
from ckanext.defrareports.commands.check_broken_resources import check_dataset_resources_job


class TestBrokenResources(BaseTestCase):
    """
    Test the broken resources command and associated job
    """
    def __init__(self):
        super(TestBrokenResources, self).__init__()
        self.dataset = {
            'resources': [{
                'id': 'test',
                'url': 'http://test.com',
                'link_status': None,
            }]
        }

    @mock.patch('requests.head')
    @mock_action('resource_patch')
    def test_active_resource_link(self, mock_requests, mock_resource_patch):
        mock_requests.return_value.status_code = 200
        check_dataset_resources_job(self.dataset)
        call_args = mock_resource_patch.call_args[0][1]
        assert_in('link_status_last_check', call_args)
        assert_equal(call_args['id'], 'test')
        assert_equal(call_args['link_status'], 'active')

    @mock.patch('requests.head')
    @mock_action('resource_patch')
    def test_inactive_resource_link(self, mock_requests, mock_resource_patch):
        mock_requests.return_value.status_code = 404
        check_dataset_resources_job(self.dataset)
        call_args = mock_resource_patch.call_args[0][1]
        assert_in('link_status_last_check', call_args)
        assert_equal(call_args['id'], 'test')
        assert_equal(call_args['link_status'], 'dead')

    @mock.patch('requests.head', side_effect=RequestException())
    @mock_action('resource_patch')
    def test_inactive_resource_link(self, mock_requests, mock_resource_patch):
        check_dataset_resources_job(self.dataset)
        call_args = mock_resource_patch.call_args[0][1]
        assert_in('link_status_last_check', call_args)
        assert_equal(call_args['id'], 'test')
        assert_equal(call_args['link_status'], 'invalid')
