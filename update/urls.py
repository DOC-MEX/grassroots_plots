from django.urls import path
from update import views

urlpatterns = [
    #path('', views.update),
    path('update/', views.selectStudy, name='selectStudy'),
    path('update/<study_id>', views.updatePlot, name='updatePlot'),
    path('plotDetails/<study_id>/<plot_id>', views.plotDetails, name='plotDetails'),
]