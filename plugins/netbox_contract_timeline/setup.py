from setuptools import setup, find_packages

setup(
    name='netbox-contract-timeline',
    version='1.0.0',
    description='NetBox plugin: horizontal timeline of Contract end dates (from netbox-contract), color-coded by urgency, filterable by Contract Type',
    author='Infraestructura',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'netbox_contract_timeline': ['templates/netbox_contract_timeline/*.html'],
    },
    install_requires=[],
)
