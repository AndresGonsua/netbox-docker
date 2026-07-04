PLUGINS = [
    "netbox_contract",
    "netbox_inventory",
    "netbox_rack_report",
]

PLUGINS_CONFIG = {
    "netbox_contract": {
        "top_level_menu": True,
    },
    "netbox_inventory": {},
    "netbox_rack_report": {
        "alert_threshold": 80,
    },
}
