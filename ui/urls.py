from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('what-is-foodlens/', views.what_is_foodlens, name='what_is_foodlens'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('hide-instruction-popup/', views.hide_instruction_popup, name='hide_instruction_popup'),
    path('get_instruction_popup_state/', views.get_instruction_popup_state, name='get_instruction_popup_state'),
    path('ajax-login/', views.ajax_login, name='ajax_login'),
    path('ajax-signup/', views.ajax_signup, name='ajax_signup'),
    path('faq/', views.faq, name="faq"),
]
