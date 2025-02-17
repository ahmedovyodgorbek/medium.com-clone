from datetime import timedelta

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh.set_exp(lifetime=timedelta(seconds=30))

    refresh.access_token.set_exp(lifetime=timedelta(seconds=10))

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }
