from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name= 'index'),
    path('about/', views.about, name= 'about'),
    path('blog/', views.blog, name= 'blog'),
    path('blog-single/', views.blog_single, name= 'blog-single'),
    path('blog/<int:id>/', views.blog_single, name='blog_single'),
    path('contact/', views.contact, name= 'contact'),
    path('gpa calculator/', views.gpa_calculator, name= 'gpa calculator'),
    path('cgpa calculator/', views.cgpa_page, name= 'cgpa calculator'),
    path('exam score predict/', views.exam_score_predict, name= 'exam score predict'),
    path('assignment_planner/', views.assignment_planner, name= 'assignment planner'),
    path('time table builder/', views.time_table_builder, name= 'time table builder'),
    path('study timer/', views.study_timer, name= 'study timer'),
    path('ai note summarizer/', views.ai_note_summarizer, name= 'ai note summarizer'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("refund-policy/", views.refund_policy, name="refund_policy"),
    path("Terms_and_Conditions/", views.Terms_and_Conditions, name="Terms_and_Conditions"),
    path('courses/', views.courses, name='courses'),
    path('course/<int:id>/', views.course_detail, name='course_detail'),

   
    path('save-cgpa/', views.save_cgpa, name='save_cgpa'),
    path('save-gpa/', views.save_gpa, name='save_gpa'),
    path("delete-gpa/<int:pk>/", views.delete_gpa, name="delete_gpa"),
    path("delete-cgpa/<int:pk>/", views.delete_cgpa, name="delete_cgpa"),
    path('download-transcript/', views.download_transcript, name='download_transcript'),
    path("download-timetable/",views.download_timetable,name="download timetable"),
    path("assignment-planner/",views.assignment_planner,name="assignment_planner"),
    path("delete-assignment/<int:id>/",views.delete_assignment,name="delete_assignment"),
    path("update-status/<int:id>/",views.update_status,name="update_status"),
    path("delete-all-assignments/", views.delete_all_assignments, name="delete_all_assignments"),
    path('edit-assignment/<int:id>/',views.edit_assignment,name='edit_assignment'),
    
    path("delete-timetable/<int:id>/", views.delete_timetable),
    path("delete-all-timetable/", views.delete_all_timetables),
    path("save-study-session/",views.save_study_session,name="save-study-session"),
    path("delete-study-session/<int:id>/", views.delete_study_session, name="delete_study_session"),
    path("clear-study-sessions/", views.clear_study_sessions, name="clear_study_sessions"),
    
    path("summarize-notes/",views.summarize_notes,name="summarize_notes"),
    path("generate-quiz/",views.generate_quiz,name="generate_quiz"),
    path("history_detail/<int:pk>/", views.history_detail, name="history_detail"),
    path("clear_aihistory/", views.clear_aihistory, name="clear_aihistory"),
    path("explain-topic/", views.explain_topic, name="explain_topic"),
    
    path("credits/", views.credits_page, name="credits"),
    path("buy-ai-credits", views.buy_ai_credits, name="buy_ai_credits"),
    path("paystack-webhook", views.paystack_webhook, name="paystack_webhook"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("student-profile/",views.student_profile,name="student_profile"),
    
   
]
