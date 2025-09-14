import os
import time
import aiohttp
from loguru import logger
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

TASKON_BASE_URL = os.getenv('TASKON_BASE_URL', 'https://api.taskon.xyz')

class TaskonError(Exception):
    def __init__(self, response_json: dict):
        self.code = response_json.get('code')
        self.message = response_json.get('message')
        super().__init__(f'(code={self.code}) {self.message}')

class UserInfo(BaseModel):
    id: int
    user_name: str

class TaskonAPI:
    def __init__(self, session: aiohttp.ClientSession, auth_token: str | None = None):
        self.session = session
        self._headers = {'content-type': 'application/json'}
        if auth_token:
            self.set_auth_token(auth_token)

    def set_auth_token(self, token: str):
        self._headers['authorization'] = token

    async def _handle(self, resp: aiohttp.ClientResponse):
        data = await resp.json()
        if data.get('error'):
            raise TaskonError(data['error'])
        return data.get('result')

    async def request_nonce(self) -> str:
        url = f'{TASKON_BASE_URL}/v1/requestChallenge'
        payload = {'ver':'1.0','type':'ClientHello','action':0}
        async with self.session.post(url, json=payload, headers=self._headers) as r:
            result = await self._handle(r)
            return result['nonce']

    async def request_auth_token(self, address: str, signature: str, nonce: str, timestamp: int, invite_code: str | None = None) -> str:
        url = f'{TASKON_BASE_URL}/v1/submitChallenge'
        did = address.replace('0x','did:etho:')
        payload = {
            'ver':'1.0','type':'ClientResponse','nonce':nonce,'did':did,
            'proof':{'type':'ES256','verificationMethod':f'{did}#key-1','created':timestamp,'value':signature},
            'VPs':[], 'invite_code': invite_code or ''
        }
        async with self.session.post(url, json=payload, headers=self._headers) as r:
            result = await self._handle(r)
            return result['token']

    async def request_user_info(self) -> UserInfo:
        url = f'{TASKON_BASE_URL}/v1/getUserInfo'
        async with self.session.post(url, headers=self._headers) as r:
            result = await self._handle(r)
            return UserInfo.model_validate(result)

async def demo_auth_flow(session: aiohttp.ClientSession, address: str, sign_fn, invite_code: str | None = None) -> str:
    api = TaskonAPI(session)
    nonce = await api.request_nonce()
    timestamp = int(time.time())
    message = {
        'type': 'ClientResponse',
        'server': {'name':'taskon_server','url':'https://taskon.xyz'},
        'nonce': nonce,
        'did': address.replace('0x','did:etho:'),
        'created': timestamp
    }
    signature = sign_fn(message)
    token = await api.request_auth_token(address, signature, nonce, timestamp, invite_code=invite_code)
    api.set_auth_token(token)
    info = await api.request_user_info()
    logger.info(f'Authenticated as {info.user_name} (id={info.id})')
    return token
