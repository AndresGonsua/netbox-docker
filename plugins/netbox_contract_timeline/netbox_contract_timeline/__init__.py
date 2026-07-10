from netbox.plugins import PluginConfig


class NetboxContractTimelineConfig(PluginConfig):
    name = 'netbox_contract_timeline'
    verbose_name = 'Contract Timeline'
    description = 'Horizontal timeline of Contract end dates (from netbox-contract), color-coded by urgency'
    version = '1.0.0'
    author = 'Infraestructura'
    base_url = 'contract-timeline'
    # This plugin reads data from netbox_contract's models (Contract, ContractType,
    # ContractAssignment). netbox_contract must be installed and listed in PLUGINS.
    default_settings = {
        # Thresholds in months. Below red_max -> red, below orange_max -> orange,
        # below yellow_max -> yellow, at or above yellow_max -> green.
        'red_max_months': 8,
        'orange_max_months': 12,
        'yellow_max_months': 18,
    }


config = NetboxContractTimelineConfig
