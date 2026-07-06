PLUGINS = [
    "netbox_contract",
    "netbox_inventory",
    "netbox_rack_report",
    "netbox_lifecycle",
]

PLUGINS_CONFIG = {
    "netbox_contract": {
        "top_level_menu": True,
    },
    "netbox_inventory": {},
    "netbox_rack_report": {
        "alert_threshold": 80,
    },
    "netbox_lifecycle": {
        "lifecycle_card_position": "right_page",
        "contract_card_position": "right_page",
    },
}
