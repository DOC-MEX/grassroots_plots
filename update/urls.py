from django.urls import path
from update import views

urlpatterns = [
    #path('', views.update),
    path('display/', views.selectStudy, name='selectStudy'),
    path('display/<study_id>', views.updatePlot, name='updatePlot'),
    path('plotDetails/<study_id>/<plot_id>', views.plotDetails, name='plotDetails'),
    path('updateDetails/<study_id>/<plot_id>', views.updateDetails, name='updateDetails'),
    path('ajax/interact_backend/', views.interact_with_apache),
    path('ajax/interact_queen/', views.interact_with_queen)
]
