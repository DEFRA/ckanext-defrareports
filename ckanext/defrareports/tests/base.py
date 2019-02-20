import ckan.plugins
from ckan import model
from nose.tools import assert_equal


class BaseTest(object):
    """
    Test that the various report pages load successfully
    """
    @classmethod
    def setup_class(cls):
        if not ckan.plugins.plugin_loaded('defrareports'):
            ckan.plugins.load('defrareports')

    def teardown(self):
        # Rebuild ckan db after each test
        model.repo.debuild_db()

    @classmethod
    def teardown_class(cls):
        # Unload the plugin after all tests have run
        ckan.plugins.unload('defrareports')

    def test_resource_delete_editor(self):
        assert_equal(1, 2)
