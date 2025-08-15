def save_google_names(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        user.first_name = response.get('given_name', '')
        user.last_name = response.get('family_name', '')
        user.save()