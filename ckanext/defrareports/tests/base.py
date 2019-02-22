import ckan.lib.create_test_data as ctd
from ckan.tests.helpers import FunctionalTestBase
from ckanext.harvest.model import setup as db_setup


class BaseTest(FunctionalTestBase):
    """
    Test that the various report pages load successfully
    """
    _load_plugins = ['harvest']

    @classmethod
    def setup_class(cls):
        super(BaseTest, cls).setup_class()
        ctd.CreateTestData.create()

    def setup(self):
        super(BaseTest, self).setup()
        db_setup()
