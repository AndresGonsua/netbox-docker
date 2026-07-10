from netbox.plugins.navigation import PluginMenu, PluginMenuItem

menu = PluginMenu(
    label='Contract Timeline',
    groups=(
        (
            'Contracts',
            (
                PluginMenuItem(
                    link='plugins:netbox_contract_timeline:timeline',
                    link_text='Expiration Timeline',
                    permissions=['netbox_contract.view_contract'],
                ),
            ),
        ),
    ),
    icon_class='mdi mdi-calendar-clock-outline',
)
