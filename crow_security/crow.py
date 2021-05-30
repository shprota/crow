import aiohttp

from . import urls
import logging
import json
from typing import Any

_LOGGER = logging.getLogger(__name__)


class Error(Exception):
    pass


class RequestError(Error):
    pass


class CrowLoginError(Error):
    pass


class CrowWsError(Error):
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


async def _validate_response(response):
    """ Verify that response is OK """
    if response.status < 400:
        return
    raise ResponseError(response.status, await response.text())


class Panel(object):
    def __init__(self, session, mac):
        self._session: Session = session
        self.id = None
        self.mac = mac
        self.name = None

    @classmethod
    async def create(cls, session, mac):
        self = Panel(session, mac)
        panel = await session.get_panel_data(mac)
        self.__dict__.update(panel)
        return self

    def __str__(self):
        return "{}-{} ({})".format(self.id, self.name, self.mac)

    def get_zones(self):
        return self._session.get_zones(self.id)

    def get_outputs(self):
        return self._session.get_outputs(self.id)

    def set_output_state(self, output_id, state):
        return self._session.set_output_state(self, output_id, state)

    def get_areas(self):
        return self._session.get_areas(self.id)

    def get_area(self, area_id):
        return self._session.get_area(self.id, area_id)

    def set_area_state(self, area_id, state):
        return self._session.set_area_state(self, area_id, state)

    def get_measurements(self):
        return self._session.get_measurements(self.id)

    def get_pictures(self, zone_id, page_size=1, page=1):
        return self._session.get_pictures(self.id, zone_id, page_size, page)

    def capture_cam_image(self, zone_id):
        return self._session.capture_cam_image(self.id, zone_id)

    def ws_connect(self, datacb):
        return self._session.ws_connect(self, datacb)


class Session(object):

    def __init__(self, email, password):
        self._email = email
        self._password = password
        self._raw_token = None
        self._token = None
        self._refresh_token = None
        self._ws_connection = None
        self.aio_session = aiohttp.ClientSession()

    async def __aenter__(self):
        await self.login()
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def _get(self, url, params=None, retry=True):
        if not self._token:
            await self.login()
        _headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Authorization': self._token
        }
        async with self.aio_session.get(url, params=params, headers=_headers) as response:
            if response.status in (400, 401) and retry:
                await self.login()
                return self._get(url, params, retry=False)
            await _validate_response(response)
            return await response.json()

    async def _patch(self, url, retry=True, headers=None, **kwargs):
        _headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Authorization': self._token
        }
        if headers:
            _headers.update(headers)

        async with self.aio_session.patch(url, headers=_headers, **kwargs) as response:
            # response = requests.patch(url, headers=_headers, **kwargs)
            if response.status in (400, 401) and retry:
                await self.login()
                return self._patch(url, headers=_headers, retry=False, **kwargs)
            await _validate_response(response)
            return await response.json()

    async def _post(self, url, retry=True, headers=None, **kwargs):
        _headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Authorization': self._token
        }
        if headers:
            _headers.update(headers)

        async with self.aio_session.post(url, headers=_headers, **kwargs) as response:
            if response.status in (400, 401) and retry:
                await self.login()
                return self._post(url, headers=_headers, retry=False, **kwargs)
            await _validate_response(response)
            return await response.json()

    def get_panel_data(self, mac):
        return self._get(urls.panel(mac))

    async def login(self):
        print('Login attempt: %s:%s' % (self._email, self._password))
        data = urls.login_data(self._email, self._password)
        async with self.aio_session.post(urls.login(), data=data) as response:
            await _validate_response(response)
            data = await response.json()
            self._raw_token = data.get('access_token')
            self._token = data.get('token_type') + ' ' + self._raw_token
            self._refresh_token = data.get('refresh_token', self._refresh_token)

    def logout(self):
        self._token = None
        self._refresh_token = None

    def get_panels(self):
        return self._get(urls.panels())

    def get_panel(self, mac):
        return Panel.create(self, mac)

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

    async def get_pictures(self, panel_id, zone_id, page_size=1, page=1):
        resp = await self._get(urls.pictures(panel_id, zone_id, page_size, page))
        return resp.get('results')

    async def download_picture(self, picture, file_name):
        url = picture.get("url")
        async with self.aio_session.get(url) as response:
            await _validate_response(response)
            with open(file_name, 'wb') as image_file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    image_file.write(chunk)

    async def capture_cam_image(self, panel_id, zone_id):
        await self._post(urls.take_picture(panel_id, zone_id))

    async def ws_connect(self, panel, datacb):
        async with self.aio_session.ws_connect(urls.ws()) as ws:
            await ws.send_json({'type': 'authentication', 'value': self._raw_token})
            msg = await ws.receive_json()
            if msg['status'] != 'OK':
                raise CrowLoginError('Authentication error: {}'.format(msg['description']))
            await ws.send_json({'type': 'subscribe', 'value': panel})
            msg: Any = await ws.receive_json()
            if msg['status'] == 'OK':
                print('Subscribed on event for panel {}'.format(panel))
            else:
                raise CrowWsError('Subscription error: {}'.format(msg['description']))

            async for msg in ws:
                # print('Received message:', msg.type, msg.data)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await datacb(data)
                if msg.type in (aiohttp.WSMsgType.CLOSED,
                                aiohttp.WSMsgType.ERROR):
                    break
