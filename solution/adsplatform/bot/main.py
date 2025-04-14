import asyncio
from . import bot_config, redis_client
from .routers import (
    campaign_create,
    campaign_list,
    campaign_delete,
    campaign_edit,
    campaign_statistics,
    my_statistics,
    commands,
    login,
    unhandled,
)
from ..config import app_config
from ..db import init_db
from datetime import timedelta

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties


async def main() -> None:
    bot = Bot(
        token=bot_config.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await init_db(
        username=app_config.postgres_user,
        password=app_config.postgres_password,
        db_name=app_config.postgres_db,
    )

    dp.include_routers(
        login.router,
        campaign_create.router,
        campaign_list.router,
        campaign_delete.router,
        campaign_edit.router,
        campaign_statistics.router,
        my_statistics.router,
        commands.router,
        unhandled.router,
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    dp = Dispatcher(
        storage=RedisStorage(
            redis=redis_client,
            state_ttl=timedelta(hours=bot_config.state_ttl_hours),
            data_ttl=timedelta(hours=bot_config.data_ttl_hours),
        )
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
