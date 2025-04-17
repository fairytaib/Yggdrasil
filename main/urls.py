"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import TemplateView
# main/urls.py  (Root‑URLConf)
from django.conf.urls import handler404, handler500
from django.shortcuts import render


def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)

handler404 = "main.urls.custom_404"
handler500 = "main.urls.custom_500"


urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("accounts/", include("allauth.urls")),
    path('admin/', admin.site.urls),
    path("contact/",
         TemplateView.as_view(template_name="contact.html"),
         name="contact"),
    path("privacy_policy/",
         TemplateView.as_view(template_name="privacy_policy.html"),
         name="privacy_policy"),
    path("faq/",
         TemplateView.as_view(template_name="faq.html"), name="faq"),
    path("legal_notice/",
         TemplateView.as_view(template_name="legal_notice.html"),
         name="legal_notice"),
    path("family_view/", include("familytree.urls")),
    path('people_of_history/',
         include("peopleOfHistory.urls"),
         name="people_of_history"),
]
