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

class TaskInfo(BaseModel):
    id: int
    template_id: str
    params: str | None = None

class CampaignInfo(BaseModel):
    id: int
    name: str
    tasks: list[TaskInfo] | None = None

class WinnerInfo(BaseModel):
    user_id: int
    user_address: str
    user_name: str
    amount: str | None = None

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

    async def request_campaign_info(self, campaign_id: int) -> CampaignInfo:
        url = f'{TASKON_BASE_URL}/v1/getCampaignInfo'
        data = str(campaign_id)
        async with self.session.post(url, data=data, headers=self._headers) as r:
            result = await self._handle(r)
            return CampaignInfo.model_validate(result)

    async def request_campaign_status_info(self, campaign_id: int) -> dict:
        url = f'{TASKON_BASE_URL}/v1/getCampaignStatusInfo'
        payload = {'id': campaign_id}
        async with self.session.post(url, json=payload, headers=self._headers) as r:
            return await self._handle(r)

    async def request_user_campaign_status(self, campaign_id: int) -> dict:
        url = f'{TASKON_BASE_URL}/v1/getUserCampaignStatus'
        data = str(campaign_id)
        async with self.session.post(url, data=data, headers=self._headers) as r:
            return await self._handle(r)

    async def check_user_campaign_eligibility(self, campaign_id: int) -> bool:
        url = f'{TASKON_BASE_URL}/v1/checkUserCampaignEligibility'
        data = str(campaign_id)
        async with self.session.post(url, data=data, headers=self._headers) as r:
            result = await self._handle(r)
            return bool(result.get('result'))

    async def request_campaign_winners(self, campaign_id: int, page: int = 0, size: int = 50) -> list[WinnerInfo]:
        url = f'{TASKON_BASE_URL}/v1/getCampaignWinners'
        payload = {"id": campaign_id, "page": {"page_no": page, "size": size}}
        async with self.session.post(url, json=payload, headers=self._headers) as r:
            result = await self._handle(r)
            data = result.get('data') or []
            return [WinnerInfo.model_validate(w) for w in data]

    async def submit_task(self, task_id: int, value: str | None = None, pre_submit: bool = False) -> bool:
        url = f'{TASKON_BASE_URL}/v1/submitTask'
        payload = {"task_id": task_id, "value": value or "", "pre_submit": pre_submit}
        async with self.session.post(url, json=payload, headers=self._headers) as r:
            return await self._handle(r)

    async def submit_campaign(self, campaign_id: int, g_captcha_response: str | None = None) -> bool:
        url = f'{TASKON_BASE_URL}/v1/submitCampaign'
        payload = {"campaign_id": campaign_id, "auto_follow_owner": False}
        if g_captcha_response:
            payload["google_recaptcha"] = g_captcha_response
        async with self.session.post(url, json=payload, headers=self._headers) as r:
            return await self._handle(r)

    async def bind_app(self, app_type: str, bind_code: str) -> None:
        url = f"{TASKON_BASE_URL}/v1/bindSNS"
        payload = {"sns_type": app_type, "token": bind_code}
        async with self.session.post(url, json=payload, headers=self._headers) as r:
            await self._handle(r)

    async def bind_twitter(self, bind_code: str) -> None:
        await self.bind_app("Twitter", bind_code)

    async def bind_discord(self, bind_code: str) -> None:
        await self.bind_app("Discord", bind_code)

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
