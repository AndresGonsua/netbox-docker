from netbox.plugins import PluginConfig


class NetboxRackReportConfig(PluginConfig):
    name = 'netbox_rack_report'
    verbose_name = 'Rack Report'
    description = 'Rack utilization report by Site, Device Role and Tenant'
    version = '1.0.0'
    author = 'Infraestructura'
    base_url = 'rack-report'
    default_settings = {
        'alert_threshold': 80,
    }


config = NetboxRackReportConfig
