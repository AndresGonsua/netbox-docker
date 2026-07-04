import io
from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render

from dcim.models import Site, Rack, Device, DeviceRole
from tenancy.models import Tenant

try:
    from netbox.plugins import get_plugin_config
    ALERT_THRESHOLD = get_plugin_config('netbox_rack_report', 'alert_threshold')
except Exception:
    ALERT_THRESHOLD = 80


def compute_utilization():
    """
    Computes rack utilization by Site, Device Role and Tenant.
    Returns a list of dicts with the data for the report.
    """
    # Total U capacity per site (sum of u_height of racks)
    site_total_u = defaultdict(float)
    site_rack_count = defaultdict(int)
    site_rack_ids = defaultdict(list)

    for rack in Rack.objects.select_related('site').all():
        sid = rack.site_id
        site_total_u[sid] += float(rack.u_height or 0)
        site_rack_count[sid] += 1
        site_rack_ids[sid].append(rack.pk)

    # Used U and counts per site / role / tenant
    site_used_u = defaultdict(float)
    site_device_count = defaultdict(int)
    site_role = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'u': 0.0}))
    site_tenant = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'u': 0.0}))

    qs = Device.objects.select_related(
        'site', 'rack', 'device_type', 'role', 'tenant'
    ).exclude(rack__isnull=True)

    for device in qs:
        sid = device.site_id
        u_height = float(device.device_type.u_height if device.device_type else 0)
        role_name = device.role.name if device.role else 'No role'
        tenant_name = device.tenant.name if device.tenant else 'No tenant'

        site_device_count[sid] += 1
        site_used_u[sid] += u_height or 0

        site_role[sid][role_name]['count'] += 1
        site_role[sid][role_name]['u'] += u_height or 0

        site_tenant[sid][tenant_name]['count'] += 1
        site_tenant[sid][tenant_name]['u'] += u_height or 0

    # Build result
    sites = {s.pk: s for s in Site.objects.all()}
    results = []

    for sid in sorted(site_total_u.keys(), key=lambda x: sites.get(x).name if sites.get(x) else ''):
        site = sites.get(sid)
        if not site:
            continue

        total_u = site_total_u[sid]
        used_u = site_used_u.get(sid, 0)
        free_u = total_u - used_u
        pct = round((used_u / total_u * 100), 1) if total_u else 0
        alert = pct >= ALERT_THRESHOLD

        results.append({
            'site': site,
            'rack_count': site_rack_count[sid],
            'device_count': site_device_count.get(sid, 0),
            'total_u': total_u,
            'used_u': used_u,
            'free_u': free_u,
            'pct': pct,
            'alert': alert,
            'roles': dict(sorted(site_role[sid].items())),
            'tenants': dict(sorted(site_tenant[sid].items())),
        })

    return results


class RackReportView(LoginRequiredMixin, View):
    template_name = 'netbox_rack_report/rack_report.html'

    def get(self, request):
        results = compute_utilization()
        total_u = sum(r['total_u'] for r in results)
        used_u = sum(r['used_u'] for r in results)
        alerts = [r for r in results if r['alert']]

        return render(request, self.template_name, {
            'results': results,
            'total_u': total_u,
            'used_u': used_u,
            'free_u': total_u - used_u,
            'total_pct': round(used_u / total_u * 100, 1) if total_u else 0,
            'total_devices': sum(r['device_count'] for r in results),
            'total_racks': sum(r['rack_count'] for r in results),
            'alerts': alerts,
            'alert_threshold': ALERT_THRESHOLD,
        })


class RackReportExportView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
        except ImportError:
            return HttpResponse('openpyxl is not installed. Run: pip install openpyxl', status=500)

        results = compute_utilization()

        wb = openpyxl.Workbook()

        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill('solid', fgColor='1F4E5F')
        warn_fill = PatternFill('solid', fgColor='FFECB3')
        danger_fill = PatternFill('solid', fgColor='FFCDD2')
        thin = Side(style='thin', color='CCCCCC')
        border = Border(top=thin, bottom=thin, left=thin, right=thin)
        center = Alignment(horizontal='center', vertical='center')

        def style_header(ws, row, ncols):
            for c in range(1, ncols + 1):
                cell = ws.cell(row=row, column=c)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center
                cell.border = border

        def autosize(ws):
            for col in ws.columns:
                length = max((len(str(c.value)) if c.value else 0) for c in col)
                ws.column_dimensions[get_column_letter(col[0].column)].width = min(max(length + 3, 12), 45)

        # Sheet 1: Summary
        ws1 = wb.active
        ws1.title = 'Summary by Site'
        headers1 = ['Site', 'Racks', 'Devices', 'Total U', 'Used U', 'Free U', '% Utilization', 'Alert']
        ws1.append(headers1)
        style_header(ws1, 1, len(headers1))

        for i, r in enumerate(results, start=2):
            ws1.append([
                r['site'].name,
                r['rack_count'],
                r['device_count'],
                r['total_u'],
                r['used_u'],
                r['free_u'],
                r['pct'],
                f"⚠️ > {ALERT_THRESHOLD}%" if r['alert'] else '✓ OK',
            ])
            if r['alert']:
                for c in range(1, len(headers1) + 1):
                    ws1.cell(row=i, column=c).fill = danger_fill
            for c in range(1, len(headers1) + 1):
                ws1.cell(row=i, column=c).border = border
        autosize(ws1)
        ws1.freeze_panes = 'A2'

        # Sheet 2: By Role
        ws2 = wb.create_sheet('By Device Role')
        headers2 = ['Site', 'Device Role', 'Devices', 'Used U']
        ws2.append(headers2)
        style_header(ws2, 1, len(headers2))
        row_idx = 2
        for r in results:
            for role, vals in r['roles'].items():
                ws2.append([r['site'].name, role, vals['count'], vals['u']])
                for c in range(1, len(headers2) + 1):
                    ws2.cell(row=row_idx, column=c).border = border
                row_idx += 1
        autosize(ws2)
        ws2.freeze_panes = 'A2'

        # Sheet 3: By Tenant
        ws3 = wb.create_sheet('By Tenant')
        headers3 = ['Site', 'Tenant', 'Devices', 'Used U']
        ws3.append(headers3)
        style_header(ws3, 1, len(headers3))
        row_idx = 2
        for r in results:
            for tenant, vals in r['tenants'].items():
                ws3.append([r['site'].name, tenant, vals['count'], vals['u']])
                for c in range(1, len(headers3) + 1):
                    ws3.cell(row=row_idx, column=c).border = border
                row_idx += 1
        autosize(ws3)
        ws3.freeze_panes = 'A2'

        # Return the file
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="rack_utilization_report.xlsx"'
        return response
