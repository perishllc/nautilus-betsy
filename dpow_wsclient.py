import asyncio
import os
import json

from aiohttp import log, ClientSession, WSMsgType, WSMessage, web

class DPOWClient():
    def __init__(self, dpow_url : str, user : str, key : str, app : web.Application):
        self.dpow_url = dpow_url
        self.user = user
        self.key = key
        self.id = 0
        self.app = app
        self.ws = None # None when socket is closed

    async def open_connection(self):
        """Create the websocket connection to dPOW service"""
        session = ClientSession()
        async with session.ws_connect(self.dpow_url) as ws:
            self.ws = ws
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    if msg.data == 'close':
                        await ws.close()
                    else:
                        # Handle Reply
                        log.server_logger.debug(f'WS Message Received {msg.data}')
                        msg_json = json.loads(msg.data)
                        await self.app['redis'].lpush(f'dpow_{msg_json["id"]}', msg.data)
                elif msg.type == WSMsgType.CLOSE:
                    log.server_logger.info('WS Connection closed normally')
                    break
                elif msg.type == WSMsgType.ERROR:
                    log.server_logger.info('WS Connection closed with error %s', ws.exception())
                    break

    async def request_work(self, hash: str) -> int:
        """Request work, return ID of the request"""
        if self.ws is None:
            raise Exception(f"Connection to {self.dpow_url} closed")
        req = {
            "user": self.user,
            "api_key": self.key,
            "hash": hash,
            "id": self.id
        }
        self.ws.send_str(json.dumps(req))
        self.id += 1
        return self.id