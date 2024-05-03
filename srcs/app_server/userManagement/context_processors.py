import os


def export_vars(request):
    return {
        'OAUTH_CLIENT_ID': os.environ.get('OAUTH_CLIENT_ID'),
        'OAUTH_CLIENT_SECRET': os.environ.get('OAUTH_CLIENT_SECRET'),
        'OAUTH_CALLBACK_URL': os.environ.get('OAUTH_CALLBACK_URL'),
    }