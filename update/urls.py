from django.urls import path
from update import views

urlpatterns = [
    #path('', views.update),
    path('display/', views.selectStudy, name='selectStudy'),
    path('display/<study_id>', views.updatePlot, name='updatePlot'),
    path('plotDetails/<study_id>/<plot_id>', views.plotDetails, name='plotDetails'),
]
