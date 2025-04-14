from ..config import BotConfig
from ..clients.api import APIClient

import redis.asyncio as redis

bot_config = BotConfig()

api_client = APIClient(base_url=bot_config.api_url)
redis_client = redis.Redis(host='redis', port=6379)
