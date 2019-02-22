from ckan.tests.helpers import mock_action
from nose.tools import assert_true

from base import BaseTestCase
from ckanext.defrareports.lib import reports

# FIXME: Once reports have been updated update these tests


class TestCaseDefraReports(BaseTestCase):
    """
    Test that the various reports load successfully and are added to the catalog
    """

    @mock_action('package_create')
    def test_publishing_report(self, mock_package_create):
        report = reports.publishing_reports.publishing_history_report['generate']()
        assert_true(mock_package_create.called_once)

    @mock_action('package_create')
    def test_access_report(self, mock_package_create):
        report = reports.access_reports.access_history_report['generate']()
        assert_true(mock_package_create.called_once)

    @mock_action('package_create')
    def test_broken_records_report(self, mock_package_create):
        report = reports.broken_resource_reports.broken_resource_report['generate']()
        assert_true(mock_package_create.called_once)

    @mock_action('package_create')
    def test_system_stats(self, mock_package_create):
        report = reports.system_stats_report['generate']()
        assert_true(mock_package_create.called_once)
