import requests

from . import urls
import logging
import json

_LOGGER = logging.getLogger(__name__)


class Error(Exception):
    pass


class RequestError(Error):
    pass


class LoginError(Error):
    pass


class ResponseError(Error):
    def __init__(self, status_code, text):
        super(ResponseError, self).__init__(
            'Invalid response'
            ', status code: {0} - Data: {1}'.format(
                status_code,
                text))
        self.status_code = status_code
        self.text = text


def _validate_response(response):
    """ Verify that response is OK """
    if response.status_code == 200:
        return
    raise ResponseError(response.status_code, response.text)


class Panel(object):
    def __init__(self, session, mac):
        self._session = session
        panel = session._get_panel(mac)
        self.__dict__.update(panel)

    def __str__(self):
        return "{}-{} ({})".format(self.id, self.name, self.mac)

    def get_zones(self):
        return self._session.get_zones(self.id)

    def get_outputs(self):
        return self._session.get_outputs(self.id)

    def set_output_state(self, output_id, state):
        self._session.set_output_state(self, output_id, state)

    def get_areas(self):
        return self._session.get_areas(self.id)

    def get_area(self, area_id):
        return  self._session.get_area(self.id, area_id)

    def set_area_state(self, area_id, state):
        self._session.set_area_state(self, area_id, state)

    def get_measurements(self):
        return self._session.get_measurements(self.id)


class Session(object):

    def __init__(self, email, password):
        self._email = email
        self._password = password
        self._token = None
        self._refresh_token = None

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.logout()
        pass

    def _get(self, url, params=None, retry=True):
        try:
            _headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Authorization': self._token
            }
            response = requests.get(url, params=params, headers=_headers)
            if response.status_code == 401:
                if retry:
                    self.login(True)
                    return self._get(url, params, retry=False)
            _validate_response(response)
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        return response.json()

    def _patch(self, url, retry=True, headers=None, **kwargs):
        try:
            _headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Authorization': self._token
            }
            if headers:
                _headers.update(headers)

            response = requests.patch(url, headers=_headers, **kwargs)
            if response.status_code == 401:
                if retry:
                    self.login(True)
                    return self._patch(url, headers=_headers, retry=False, **kwargs)
            _validate_response(response)
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        return response.json()



    def _get_panel(self, mac):
        return self._get(urls.panel(mac))

    def login(self, refresh=False):
        try:
            data = urls.login_data(self._email, self._password)
            if refresh and self._refresh_token:
                data = urls.refresh_data(self._refresh_token)
            response = requests.post(urls.login(), data=data)
            _validate_response(response)
        except requests.exceptions.RequestException as ex:
            raise RequestError(ex)
        data = response.json()
        self._token = data.get('token_type') + ' ' + data.get('access_token')
        self._refresh_token = data.get('refresh_token', self._refresh_token)



    def logout(self):
        self._token = None
        self._refresh_token = None

    def get_panels(self):
        return self._get(urls.panels())

    def get_panel(self, mac):
        return Panel(self, mac)

    def get_zones(self, panel_id):
        return self._get(urls.zones(panel_id))

    def get_outputs(self, panel_id):
        return self._get(urls.outputs(panel_id))

    def set_output_state(self, panel, output_id, state):
        return self._patch(urls.output(panel.id, output_id),
                           json={"state": state},
                           headers={
                               "X-Crow-CP-Remote": panel.remote_access_password,
                               "X-Crow-CP-User": panel.user_code,
                           })


    def get_areas(self, panel_id):
        return self._get(urls.areas(panel_id))

    def get_area(self, panel_id, area_id):
        return self._get(urls.area(panel_id, area_id))

    def set_area_state(self, panel, area_id, state):
        return self._patch(urls.area(panel.id, area_id),
                           json={"state": state, "force": False},
                           headers={
                               "X-Crow-CP-Remote": panel.remote_access_password,
                               "X-Crow-CP-User": panel.user_code
                           })

    def get_measurements(self, panel_id):
        return self._get(urls.measurements(panel_id))