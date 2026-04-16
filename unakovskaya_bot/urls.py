"""
URL configuration for unakovskaya_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from unakovskaya_bot.app import internal_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('internal-api/users/sync/', internal_api.users_sync),
    path(
        'internal-api/users/<str:platform>/<int:user_id>/is-admin/',
        internal_api.user_is_admin,
    ),
    path(
        'internal-api/users/<str:platform>/<int:user_id>/set-admin/',
        internal_api.user_set_admin,
    ),
    path(
        'internal-api/users/<str:platform>/<int:user_id>/unset-admin/',
        internal_api.user_unset_admin,
    ),
    path(
        'internal-api/users/<str:platform>/<int:user_id>/email/',
        internal_api.user_add_email,
    ),
    path('internal-api/users/tg/ids/', internal_api.tg_user_ids),
    path('internal-api/reports/emails/', internal_api.report_emails),
    path('internal-api/settings/email-step/', internal_api.email_step_view),
    path('internal-api/settings/email-text/', internal_api.email_text_view),
    path('internal-api/links/', internal_api.links_view),
    path('internal-api/links/active/', internal_api.active_links_view),
    path('internal-api/links/<int:link_id>/', internal_api.links_delete),
]
