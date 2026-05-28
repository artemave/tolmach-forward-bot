from bot.db import Database, User


def _user(*, target_language: str | None, level: str | None) -> User:
    return User(
        user_id=1,
        target_language=target_language,
        level=level,
        last_original=None,
        last_translation=None,
        created_at="2026-05-27T00:00:00+00:00",
        updated_at="2026-05-27T00:00:00+00:00",
    )


def test_is_configured_true_when_language_and_level_set() -> None:
    assert _user(target_language="Spanish", level="B1").is_configured is True


def test_is_configured_false_when_language_missing() -> None:
    assert _user(target_language=None, level="B1").is_configured is False


def test_is_configured_false_when_level_missing() -> None:
    assert _user(target_language="Spanish", level=None).is_configured is False


async def test_get_user_returns_none_for_unknown(database: Database) -> None:
    assert await database.get_user(999) is None


async def test_set_language_creates_then_updates(database: Database) -> None:
    await database.set_language(1, "Spanish")
    created = await database.get_user(1)
    assert created is not None
    assert created.target_language == "Spanish"
    assert created.level is None

    await database.set_language(1, "French")
    updated = await database.get_user(1)
    assert updated is not None
    assert updated.target_language == "French"


async def test_set_level_creates_then_updates(database: Database) -> None:
    await database.set_level(1, "B1")
    created = await database.get_user(1)
    assert created is not None
    assert created.level == "B1"
    assert created.target_language is None

    await database.set_level(1, "C1")
    updated = await database.get_user(1)
    assert updated is not None
    assert updated.level == "C1"


async def test_set_language_and_level_combine(database: Database) -> None:
    await database.set_language(1, "German")
    await database.set_level(1, "A2")
    user = await database.get_user(1)
    assert user is not None
    assert user.target_language == "German"
    assert user.level == "A2"
    assert user.is_configured is True


async def test_save_last_post_creates_then_updates(database: Database) -> None:
    await database.save_last_post(1, "hola", "hello")
    saved = await database.get_user(1)
    assert saved is not None
    assert saved.last_original == "hola"
    assert saved.last_translation == "hello"

    await database.save_last_post(1, "adios", "bye")
    updated = await database.get_user(1)
    assert updated is not None
    assert updated.last_original == "adios"
    assert updated.last_translation == "bye"
