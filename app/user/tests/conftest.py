def api_client_with_credentials(token: str, api_client):
    return api_client_with_credentials(HTTP_AUTHORIZATION="Bearer" + token)
    