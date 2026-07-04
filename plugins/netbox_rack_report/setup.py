from setuptools import setup, find_packages

setup(
    name='netbox-rack-report',
    version='1.0.0',
    description='NetBox plugin: Rack utilization report by Site, Role and Tenant',
    author='Infraestructura',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'netbox_rack_report': ['templates/netbox_rack_report/*.html'],
    },
    install_requires=[],
)
