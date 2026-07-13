PLUGINS = [
    "netbox_contract",
    "netbox_inventory",
    "netbox_rack_report",
    "netbox_contract_timeline",
    "netbox_topology_views",
]

PLUGINS_CONFIG = {
    "netbox_contract": {
        "top_level_menu": True,
    },
    "netbox_rack_report": {
        "alert_threshold": 80,
    },
    "netbox_contract_timeline": {
        "red_max_months": 6,
        "orange_max_months": 8,
        "yellow_max_months": 12,
    },
    "netbox_inventory": {},
    "netbox_topology_views": {},
}
