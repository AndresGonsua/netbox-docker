from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.views import View
from django.shortcuts import render

from dcim.models import Device
from netbox_contract.models import Contract, ContractType

try:
    from netbox.plugins import get_plugin_config

    def cfg(key):
        return get_plugin_config('netbox_contract_timeline', key)
except Exception:
    def cfg(key):
        defaults = {
            'red_max_months': 8,
            'orange_max_months': 12,
            'yellow_max_months': 18,
        }
        return defaults.get(key)


def get_band(months_remaining, red_max, orange_max, yellow_max):
    """
    Returns a band key based on months remaining until the contract end date.
    Already-expired contracts (negative months) are always 'red'.
    """
    if months_remaining < red_max:
        return 'red'
    elif months_remaining < orange_max:
        return 'orange'
    elif months_remaining < yellow_max:
        return 'yellow'
    else:
        return 'green'


BAND_LABELS = {
    'red': 'Critical',
    'orange': 'Warning',
    'yellow': 'Upcoming',
    'green': 'OK',
}


class ContractTimelineView(LoginRequiredMixin, View):
    template_name = 'netbox_contract_timeline/timeline.html'

    def get(self, request):
        red_max = cfg('red_max_months')
        orange_max = cfg('orange_max_months')
        yellow_max = cfg('yellow_max_months')

        today = date.today()

        selected_type_id = request.GET.get('contract_type', '')

        contracts_qs = Contract.objects.exclude(end_date__isnull=True).select_related(
            'contract_type', 'tenant'
        )

        if selected_type_id.isdigit():
            contracts_qs = contracts_qs.filter(contract_type_id=int(selected_type_id))

        device_ct = ContentType.objects.get_for_model(Device)

        items = []
        for contract in contracts_qs:
            delta_days = (contract.end_date - today).days
            months_remaining = delta_days / 30.44
            band = get_band(months_remaining, red_max, orange_max, yellow_max)

            device_assignments = contract.assignments.filter(content_type=device_ct)
            devices = [a.content_object for a in device_assignments if a.content_object is not None]

            items.append({
                'contract': contract,
                'end_date': contract.end_date,
                'months_remaining': round(months_remaining, 1),
                'band': band,
                'band_label': BAND_LABELS[band],
                'expired': delta_days < 0,
                'devices': devices,
                'device_count': len(devices),
            })

        items.sort(key=lambda x: x['end_date'])

        counts = {'red': 0, 'orange': 0, 'yellow': 0, 'green': 0}
        for item in items:
            counts[item['band']] += 1

        max_months_seen = max([i['months_remaining'] for i in items], default=yellow_max)
        axis_max = max(yellow_max + 6, max_months_seen + 2)

        for item in items:
            pct = (item['months_remaining'] / axis_max) * 100
            item['bar_pct'] = round(max(0, min(100, pct)), 1)

        raw_ticks = sorted(set([0, red_max, orange_max, yellow_max, round(axis_max)]))
        axis_ticks = [
            {'label': t, 'pct': round((t / axis_max) * 100, 1)}
            for t in raw_ticks
        ]

        contract_types = ContractType.objects.all().order_by('name')

        return render(request, self.template_name, {
            'items': items,
            'counts': counts,
            'axis_max': round(axis_max, 1),
            'axis_ticks': axis_ticks,
            'contract_types': contract_types,
            'selected_type_id': selected_type_id,
            'thresholds': {
                'red_max': red_max,
                'orange_max': orange_max,
                'yellow_max': yellow_max,
            },
        })
