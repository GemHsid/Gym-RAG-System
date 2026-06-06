from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db import connection
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.conf import settings
from django.shortcuts import render
import django
import sys
from datetime import timedelta
import json
from users.models import UserProfile
from fitness.models import Booking, CheckIn, EquipmentUsage
from bot.models import ChatMessage
from orders.models import Order

@staff_member_required
def dashboard(request):
    """
    后台管理首页仪表盘 (需管理员登录)
    """
    # 获取系统信息
    current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    django_version = django.get_version()
    python_version = sys.version.split()[0]
    startup_time = request.META.get('SERVER_START_TIME', current_time)
    
    # 获取数据库表数量 (适配 PostgreSQL 和 SQLite)
    table_count = 0
    db_engine = settings.DATABASES['default']['ENGINE']
    db_type_name = "PostgreSQL" if "postgresql" in db_engine else "SQLite"
    
    try:
        with connection.cursor() as cursor:
            if "postgresql" in db_engine:
                cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
            else:
                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
            row = cursor.fetchone()
            if row:
                table_count = row[0]
    except Exception:
        pass # Ignore db errors for welcome page
    
    # 获取真实业务指标
    today = timezone.now().date()
    today_entries = CheckIn.objects.filter(checkin_time__date=today).count()
    current_occupancy = CheckIn.objects.filter(checkout_time__isnull=True).count()
    today_bookings = Booking.objects.filter(created_at__date=today).count()
    ai_queries = ChatMessage.objects.filter(role='user', created_at__date=today).count()
    
    # 新增：付费与交易相关指标
    today_revenue = Order.objects.filter(created_at__date=today, status='PAID').aggregate(total=Sum('amount'))['total'] or 0
    total_revenue = Order.objects.filter(status='PAID').aggregate(total=Sum('amount'))['total'] or 0
    paid_orders_count = Order.objects.filter(created_at__date=today, status='PAID').count()
    
    # 新增：过去7天的营收趋势图表数据
    seven_days_ago = today - timedelta(days=6)
    revenue_trend = list(Order.objects.filter(created_at__date__gte=seven_days_ago, status='PAID')
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(daily_total=Sum('amount'))
        .order_by('date'))
        
    # 补全7天数据，防止某天没收入断层
    dates = [(seven_days_ago + timedelta(days=i)).strftime('%m-%d') for i in range(7)]
    revenue_data = {date: 0 for date in dates}
    for item in revenue_trend:
        if item['date']:
            revenue_data[item['date'].strftime('%m-%d')] = float(item['daily_total'])
            
    chart_labels = json.dumps(list(revenue_data.keys()))
    chart_values = json.dumps(list(revenue_data.values()))

    show_equipment_heatmap = getattr(settings, "DASHBOARD_SHOW_EQUIPMENT_HEATMAP", False)
    top_equipment = []
    if show_equipment_heatmap:
        usage_qs = (
            EquipmentUsage.objects.filter(started_at__date=today)
            .values("equipment__name")
            .annotate(total_minutes=Sum("duration_minutes"), cnt=Count("id"))
            .order_by("-total_minutes", "-cnt")
        )
        usage_list = list(usage_qs[:8])
        max_minutes = max([u["total_minutes"] or 0 for u in usage_list], default=0)
        for u in usage_list:
            minutes = u["total_minutes"] or 0
            rate = int(round((minutes / max_minutes) * 100)) if max_minutes > 0 else 0
            top_equipment.append({"name": u["equipment__name"], "usage_rate": rate})

    context = {
        'current_time': current_time,
        'django_version': django_version,
        'python_version': python_version,
        'table_count': table_count,
        'db_type_name': db_type_name,
        'startup_time': startup_time,
        'app_version': '2.0.0', 
        'last_updated': '2026-03-27',
        'today_entries': today_entries,
        'current_occupancy': current_occupancy,
        'today_bookings': today_bookings,
        'ai_queries': ai_queries,
        'today_revenue': today_revenue,
        'total_revenue': total_revenue,
        'paid_orders_count': paid_orders_count,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'top_equipment': top_equipment,
        'show_equipment_heatmap': show_equipment_heatmap,
        'rag_engine_text': f"RAG 检索服务 + {getattr(settings, 'LLM_MODEL', 'Qwen3-8B')}",
        'media_storage_text': 'OSS / 对象存储',
        'payment_component_text': '微信支付链路已规划，当前以项目实际接入状态为准',
    }
    
    return render(request, 'dashboard.html', context)
