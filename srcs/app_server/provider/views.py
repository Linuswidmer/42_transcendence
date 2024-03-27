import requests
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView)
from .provider import CustomProvider
from django.conf import settings


class CustomAdapter(OAuth2Adapter):
    provider_id = CustomProvider.id

    access_token_url = f'{settings.OAUTH_SERVER_BASEURL}/oauth/token'
    profile_url = f'{settings.OAUTH_SERVER_BASEURL}/v2/me'

    authorize_url = f'{settings.OAUTH_SERVER_BASEURL}/oauth/authorize'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': f'Bearer {token.token}', 'Accept':'application/json'}
        #code =  kwargs['response']['code']
        code = request.GET.get('code')
        response = requests.post(self.access_token_url, params={'code': code})
        extra_data = response.json()
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(CustomAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CustomAdapter)