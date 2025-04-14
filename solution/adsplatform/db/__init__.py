from urllib.parse import quote_plus

from tortoise import Tortoise


async def init_db(username: str, password: str, db_name: str, host: str = 'db') -> None:
    await Tortoise.init(
        db_url=f"postgres://{username}:{quote_plus(password)}@{host}:5432/{db_name}",
        modules={'models': ['adsplatform.db.models']},
    )
    await Tortoise.generate_schemas()
