from django.conf.urls import patterns, include, url
from django.db.models import Min, Count
from django.views.generic import TemplateView, ListView

from .models import Round
from .views import ScheduleView, WorksheetView

from .views import AnyListView, AnyDetailView, AnyCreateView

urlpatterns = patterns('main.views',
    url(r'^$', TemplateView.as_view(
            template_name="main/home.html")),
    url(r'^schedule/$',
        ScheduleView.as_view(),
        name="view_schedule"),
    url(r'^worksheet/$',
        WorksheetView.as_view(),
        name="view_worksheet"),
    url(r'^jobschedule/$', 'add_job_schedule'),
    url(r'^jobschedule/(\d+)/$', 'edit_job_schedule'),
    url(r'^end_of_day/$', 'end_of_day', name="end_of_day"),

    url(r'^(\w+)/$', AnyCreateView.as_view(
            template_name="main/create.html"),
        name="create_object",
        ),
    url(r'^(?P<model>\w+)/(?P<pk>\d+)/$', AnyDetailView.as_view(
            template_name="main/detail.html"),
            name="object_detail"),
)
