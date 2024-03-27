from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class CustomAccount(ProviderAccount):
    pass


class CustomProvider(OAuth2Provider):

    id = 'provider'
    name = 'ProviderOAuth2 Provider'
    account_class = CustomAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(
                    username=data['login'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    )

    #def get_default_scope(self):
        #pass


providers.registry.register(CustomProvider)