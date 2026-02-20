from django.urls import path

from .views import add_entry, add_range, delete_entry, entry_detail, month_view, toggle_entry

app_name = "leave"

urlpatterns = [
    path("", month_view, name="month"),
    path("<int:year>/<int:month>/", month_view, name="month"),
    path("add/", add_entry, name="add"),
    path("toggle/", toggle_entry, name="toggle"),
    path("add-range/", add_range, name="add_range"),
    path("<int:entry_id>/", entry_detail, name="detail"),
    path("<int:entry_id>/delete/", delete_entry, name="delete"),
]
