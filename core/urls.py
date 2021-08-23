from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from core.views import GetCountriesView
from core.views import UpdateAttachmentView
from core.views.help_scout import HelpScoutConversationsView, HelpScoutThreadsView


app_name = 'core'

urlpatterns = [
    path("countries/", GetCountriesView.as_view(), name="countries-list"),
    path("attachment/<int:pk>/", csrf_exempt(UpdateAttachmentView.as_view()), name="update-attachment"),

    path("help-scout/conversations/<int:deal_id>/", HelpScoutConversationsView.as_view(),
         name="get-helpscout-conversations-for-deal"),
    path("help-scout/conversations/<int:deal_id>/threads/<int:conversation_id>/", HelpScoutThreadsView.as_view(),
         name="get-helpscout-conversation-threads-for-deal"),
]
