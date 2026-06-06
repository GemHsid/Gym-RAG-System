from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime

class ExportExcelMixin:
    """
    通用 Excel 导出 Mixin
    在 ModelAdmin 中添加 actions = ['export_as_excel']
    """
    def export_as_excel(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={meta}.xlsx'
        
        wb = Workbook()
        ws = wb.active
        ws.title = str(meta.verbose_name)[:30] # Excel sheet title limit

        # Write header
        ws.append(field_names)

        # Write data
        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif value is None:
                    value = ''
                row.append(str(value))
            ws.append(row)

        wb.save(response)
        return response

    export_as_excel.short_description = "导出所选数据为 Excel"
