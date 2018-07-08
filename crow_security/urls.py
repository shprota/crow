"""
Crow urls.
"""

try:
    # Python 3
    from urllib.parse import quote_plus
except ImportError as e:
    # Python 2
    # noinspection PyUnresolvedReferences
    from urllib import quote_plus

BASE_URL = 'https://api.crowcloud.xyz'
WS_URL = 'wss://websocket.crowcloud.xyz'
CLIENT_ID = 't4WDssse5zzTbRlm8Vi7Evpa8ADz7g4xLiRnYOmx'
CLIENT_SECRET = 'qz8p9hcJNG6p3PJi7nZMva9M7IOOmTmhenPzMb8wV4aMQ4BIrmQpJVDIPyJK3mQ4LMYmhCwCoalQ4VRIaXXQBNvARrOpcrrO4PBxdyNiSmYOiurXULPk2C38oUVvBeAL'


def login():
    return BASE_URL + '/o/token/'


def login_data(email, password):
    return {
        "username": email,
        "password": password,
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

def refresh_data(refresh_token):
    return {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }


def panels():
    return BASE_URL + '/panels/'


def panel(mac):
    return BASE_URL + '/panels/' + mac + '/'


def zones(panel_id):
    return '{base_url}/panels/{panel_id}/zones/'.format(base_url=BASE_URL, panel_id=panel_id)

def outputs(panel_id):
    return '{base_url}/panels/{panel_id}/outputs/'.format(base_url=BASE_URL, panel_id=panel_id)

def output(panel_id, output_id):
    return '{base_url}/panels/{panel_id}/outputs/{output_id}/'.format(base_url=BASE_URL, panel_id=panel_id, output_id=output_id)


def zone(panel_id, zone_id):
    return '{base_url}/panels/{panel_id}/zones/{zone_id}/'.format(base_url=BASE_URL, panel_id=panel_id, zone_id=zone_id)


def areas(panel_id):
    return '{base_url}/panels/{panel_id}/areas/'.format(base_url=BASE_URL, panel_id=panel_id)

def area(panel_id, area_id):
    return '{base_url}/panels/{panel_id}/areas/{area_id}/'.format(base_url=BASE_URL, panel_id=panel_id, area_id=area_id)

def measurements(panel_id):
    return '{base_url}/panels/{panel_id}/dect/measurements/latest/by_zone/'.format(base_url=BASE_URL, panel_id=panel_id)

def pictures(panel_id, zone_id, page_size=1, page=1):
    return '{base_url}/panels/{panel_id}/zones/{zone_id}/pictures/?page_size={page_size}&page={page}'\
        .format(base_url=BASE_URL, panel_id=panel_id, zone_id=zone_id, page_size=page_size, page=page)

def ws():
    return '{}/sockjs/websocket'.format(WS_URL)
