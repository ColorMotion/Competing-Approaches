import requests


def _save_content(response, destination):
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(65536):
            if chunk:
                f.write(chunk)


def _get_confirm_token(response):
    return next(
        value for key, value in response.cookies.items() if key.startswith('download_warning'),
    None)


def download(id, destination):
    URL = 'https://docs.google.com/uc?export=download'

    session = requests.Session()
    params = {'id': id}
    for _ in range(2):
        response = session.get(URL, params=params, stream=True)
        token = _get_confirm_token(response)  # confirm large download
        if not token:
            break
        params['confirm'] = token

    _save_content(response, destination)
