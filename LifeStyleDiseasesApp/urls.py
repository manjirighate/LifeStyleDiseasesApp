"""
URL configuration for LifeStyleDiseasesApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import views
urlpatterns = [
    path('',views.index),
    path('home/',views.index),
    path('user/',views.user),
    path('admin/',views.admin),
    path('viewDoctors/',views.viewDoctors),
    path('doctor/',views.doctor),
    path('login/',views.login),
    path('register-doctor/',views.registerDoctor),
    path('logout/',views.logout),
    path('Cities/',views.Cities),
    path('search_doctors/',views.search_doctors),
    path('registeruser/',views.registeruser),
    path('changePass/',views.changePass),
    path('changePassReg/',views.changePassReg),
    path("diseases/", views.viewDiseases),
    path("register-disease/", views.registerDisease),
    path("lifestyle/", views.lifestyle),
    path("analyze_lifestyle/", views.analyze_lifestyle),
    path("searchSymptoms/", views.searchSymptoms),
    path("recommendDoctors/", views.recommendDoctors),
    path("doctorDetails/", views.doctorDetails),
    path("submitDoctorReview/", views.submitDoctorReview),
    path("manageSymptoms/", views.manageSymptoms, name="manageSymptoms"),
    path("manageDiseaseSymptoms/", views.manageDiseaseSymptoms, name="manageDiseaseSymptoms"),
    path("manageDoctorDiseases/", views.manageDoctorDiseases, name="manageDoctorDiseases"),
    path("manageCommonDiseases/", views.manageCommonDiseases, name="manageCommonDiseases"),
    path('manage-recommendations/', views.manage_recommendations),
    
]
