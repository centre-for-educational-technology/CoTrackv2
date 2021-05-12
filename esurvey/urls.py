from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required
from .views import CompleteForm, CREATE_FORMS
initial = {'activity_info':{'new':False}}

urlpatterns = [
    path("esurvey/collaboration/<session>/<group>", login_required(views.surveyForm), name="survey_form"),
    path("esurvey/engagement/<session>/<group>", login_required(views.engagementForm), name="engagement_form"),
    path("esurvey/usability/", login_required(views.usabilityForm), name="usability_form"),
    path("sessions/filter/<filter>", login_required(views.sessionFilter), name="session_filter"),
    path("session/<session_id>/edit", login_required(views.edit),name="edit_session"),
    path("session/<session_id>/duplicate", login_required(views.duplicate),name="duplicate_session"),
    path("sessions/new", login_required(CompleteForm.as_view(CREATE_FORMS)), name='create_session'),
    path("sessions/<session_id>/demo", login_required(views.enterForm), name='demo_session'),
    path("sessions/", login_required(views.overview), name="project_home"),  # <-- added
    path("sessions/activate/<session_id>", login_required(views.activateSession), name="session_activate"),
    path("sessions/deactivate/<session_id>", login_required(views.deactivateSession), name="session_deactivate"),
    path("sessions/download/<session_id>", login_required(views.downloadLog), name="download_log"),
    path("sessions/mapping/<session_id>", login_required(views.downloadMapping), name="download_mapping"),
    path("sessions/chat/<session_id>", login_required(views.downloadChat), name="download_chat"),
    path("sessions/vad/<session_id>", login_required(views.downloadVad), name="download_vad"),
    path("sessions/files/<session_id>", login_required(views.downloadFileTimestamp), name="download_fileTimestamp"),
    path("sessions/speech/<session_id>", login_required(views.downloadSpeech), name="download_speech"),
    path("sessions/padtext/<session_id>/<group_id>", login_required(views.getGroupText), name='group_text'),
    path("sessions/<session_id>", login_required(views.getSession), name="session_page"),
    path("enter/",login_required(views.enterForm), name="student_entry"),
    path("consent/",login_required(views.consentView), name="student_consent"),
    path("enter/pad/<group_id>",login_required(views.getPad), name="student_pad"),
    path("audio/", views.model_form_upload, name='views.model_form_upload'),
    path("audiolist/", views.list_files, name='views.list_files'),
    path("leave/",views.LeaveSession, name='leave_session'),
    #restapi
    path("getStats/<padid>", views.getGroupPadStats),
    path("getRevCount/<padid>", views.getRevCount, name='getRevisionCount'),
    path("getTime/",views.getTime,name='time'),
    path("getSpeakingStats/<session_id>", views.getSpeakingStats),
    path("getHelpQueries/<session_id>", views.getHelpQueries),
    ]
