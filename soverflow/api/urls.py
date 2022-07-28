from . views import QuestionsView
from django.urls import path

urlpatterns = [
    path('',QuestionsView.as_view())
]