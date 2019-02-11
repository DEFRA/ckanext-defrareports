import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.report.interfaces import IReport


class DefraReportsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(IReport)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IDatasetForm, inherit=True)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'fanstatic')
        toolkit.add_resource('public', 'defrareports')

    # IReport
    def register_reports(self):
        from ckanext.defrareports.lib import reports
        return [
            reports.publishing_history_report,
            reports.access_history_report,
            reports.broken_resource_report,
            reports.quality_report,
            reports.system_stats_report
        ]

    # ITemplateHelpers
    def get_helpers(self):
        from inspect import getmembers, isfunction
        import ckanext.defrareports.helpers as h
        helper_dict = {}
        functions_list = [o for o in getmembers(h, isfunction)]
        for name, fn in functions_list:
            if name[0] != '_':
                helper_dict[name] = fn
        return helper_dict

    def package_types(self):
        return []

    def _modify_resource_schema(self, schema):
        schema['resources'].update({
            'link_status': [toolkit.get_validator('ignore_missing')],
            'link_status_last_check': [toolkit.get_validator('ignore_missing')],
        })
        return schema

    def create_package_schema(self):
        schema = super(DefraReportsPlugin, self).create_package_schema()
        schema = self._modify_resource_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(DefraReportsPlugin, self).update_package_schema()
        schema = self._modify_resource_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(DefraReportsPlugin, self).show_package_schema()
        schema = self._modify_resource_schema(schema)
        return schema

