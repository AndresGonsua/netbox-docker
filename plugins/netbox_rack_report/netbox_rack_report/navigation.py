from netbox.plugins.navigation import PluginMenu, PluginMenuButton, PluginMenuItem

menu = PluginMenu(
    label='Rack Report',
    groups=(
        (
            'Utilization',
            (
                PluginMenuItem(
                    link='plugins:netbox_rack_report:rack_report',
                    link_text='Rack Utilization',
                    permissions=['dcim.view_rack'],
                ),
            ),
        ),
    ),
    icon_class='mdi mdi-chart-bar',
)
