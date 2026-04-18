from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("login/google/", views.GoogleLogin.as_view(), name="google_login"),
    path("logout/", views.GoogleLogout.as_view(), name="google-logout"),
    path("login/username/", views.UsernameLogin.as_view(), name="username-login"),
    path("startup_list/",views.StartupListView.as_view(),name='startup-list'),
    path("expert_list/",views.ExpertListView.as_view(),name='expert-list'),
    path('guided_startups/',views.StartupsUnderMentorView.as_view(),name='guided-startups'),
    path('connections/list/',views.ListConnections.as_view(),name='list-connections'),
    path('connections/send/',views.SendConnectionView.as_view(),name='send-connections'),
    path('connections/accept/',views.AcceptConnectionView.as_view(),name='accept-connections'),
    path('connections/delete/',views.DeleteConnectionView.as_view(),name='accept-connections'),
    path('profile/',views.RetrieveEditProfileView.as_view(),name="profile"),
    path('profile/startup/',views.RetrieveEditStartupView.as_view(),name="startup-profile"),
    path('search/',views.SearchProfile.as_view(),name="profile-search"),
    path('role-list/', views.RoleList.as_view(), name='role-list'),
    path('startup_detail/',views.StartupDetailView.as_view(),name="startup-detail"),
    path('profile_detail/',views.UserProfileDetailView.as_view(),name="profile-detail"),
    path('update-email/',views.UpdateEmail.as_view(),name="update-profile"),
    path('consultant-resource/interestcapture/',views.InterestCaptureView.as_view(),name='interest-capture')







]
