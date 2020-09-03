import os
import urllib
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import xarray as xr
from netrc import netrc

sessions = {}

class URSSession(requests.Session):
    def __init__(self, username=None, password=None):
        super(URSSession, self).__init__()
        self.username = username
        self.password = password
        self.original_url = None

    def authenticate(self, url):
        self.original_url = url
        super(URSSession, self).get(url)
        self.original_url = None

    def get_redirect_target(self, resp):
        if resp.is_redirect:
            if resp.headers['location'] == self.original_url:
                # Redirected back to original URL, so OAuth2 complete. Exit here
                return None
        return super(URSSession, self).get_redirect_target(resp)

    def rebuild_auth(self, prepared_request, response):
        # If being redirected to URS and we have credentials, add them in
        # otherwise default session code will look to pull from .netrc
        if "https://urs.earthdata.nasa.gov" in prepared_request.url \
                and self.username and self.password:
            prepared_request.prepare_auth((self.username, self.password))
        else:
            super(URSSession, self).rebuild_auth(prepared_request, response)
        return

class NSIDCdata:

    def get_session(self, url):
        """ Get existing session for host or create it
        """
        global sessions
        host = urllib.parse.urlsplit(url).netloc
        usr, _, auth = netrc().hosts['urs.earthdata.nasa.gov']

        if host not in sessions:
            session = requests.Session()
            if 'urs' in session.get(url).url:
                session = URSSession(useranme=usr, password=auth)
                session.authenticate(url)

            retries = Retry(total=5, connect=3, backoff_factor=1, method_whitelist=False,
                        status_forcelist=[400, 401, 403, 404, 408, 500, 502, 503,  504])
            session.mount('http', HTTPAdapter(max_retries=retries))

            sessions[host] = session

        return sessions[host]

    def get_dataset(self, url):
        """ Get single dataset from url
        """

        session = self.get_session(url)
        store = xr.backends.PydapDataStore.open(url, session=session)
        dataset = xr.open_dataset(store)


        return dataset
