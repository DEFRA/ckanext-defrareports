import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.report.interfaces import IReport


class DefraReportsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(IReport)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'defrareports')
        toolkit.add_resource('public/js', 'defrareports')

    # IReport
    def register_reports(self):
        from ckanext.defrareports.lib import reports
        return [
            reports.publishing_report,
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
