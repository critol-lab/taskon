import asyncio
import json
import os
from loguru import logger
import aiohttp
from dotenv import load_dotenv
from web3.auto import w3
from eth_account.messages import encode_defunct
from taskon.api import demo_auth_flow

load_dotenv()

PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY','')
INVITE = os.getenv('DEFAULT_INVITE_CODE')

def sign_message(message: dict) -> str:
    payload = json.dumps(message, separators=(',', ':'), ensure_ascii=False)
    msg = encode_defunct(text=payload)
    signed = w3.eth.account.sign_message(msg, private_key=PRIVATE_KEY)
    return signed.signature.hex()

async def main():
    if not PRIVATE_KEY:
        raise SystemExit('WALLET_PRIVATE_KEY not set')
    address = w3.eth.account.from_key(PRIVATE_KEY).address
    async with aiohttp.ClientSession() as session:
        token = await demo_auth_flow(session, address, sign_message, invite_code=INVITE)
        logger.success(f'TaskOn token: {token[:12]}...')

if __name__ == '__main__':
    asyncio.run(main())
