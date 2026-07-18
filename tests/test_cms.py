from __future__ import annotations

import asyncio
import io

from fastapi import UploadFile
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.app.core.settings import Settings
from backend.app.models import Base, SiteBlock
from backend.app.seed import _upsert_site_block
from backend.app.services.media import store_uploaded_image


def test_seed_does_not_overwrite_admin_content() -> None:
    asyncio.run(_assert_seed_does_not_overwrite_admin_content())


async def _assert_seed_does_not_overwrite_admin_content() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async with sessions() as db:
        await _upsert_site_block(
            db,
            {"key": "hero_title", "title": "Заголовок", "content": "Первый текст"},
            {},
        )
        await db.commit()
        block = (
            await db.execute(select(SiteBlock).where(SiteBlock.key == "hero_title"))
        ).scalar_one()
        block.content = "Текст из админки"
        await db.commit()

        await _upsert_site_block(
            db,
            {"key": "hero_title", "title": "Заголовок", "content": "Новый seed"},
            {},
        )
        await db.commit()
        block = (
            await db.execute(select(SiteBlock).where(SiteBlock.key == "hero_title"))
        ).scalar_one()
        assert block.content == "Текст из админки"

    await engine.dispose()


def test_uploaded_image_is_normalized_to_jpg_and_webp(tmp_path) -> None:
    asyncio.run(_assert_uploaded_image_is_normalized(tmp_path))


async def _assert_uploaded_image_is_normalized(tmp_path) -> None:
    source = io.BytesIO()
    Image.new("RGB", (3200, 1800), "#c93429").save(source, "PNG")
    upload = UploadFile(filename="Кухня клиента.png", file=io.BytesIO(source.getvalue()))
    settings = Settings(MEDIA_DIR=str(tmp_path), MAX_UPLOAD_MB=5)

    media = await store_uploaded_image(upload, settings, category="gallery", is_real_work=True)

    assert media.width == 2400
    assert media.height == 1350
    assert media.jpg_path and (tmp_path / media.jpg_path).is_file()
    assert media.webp_path and (tmp_path / media.webp_path).is_file()
    assert media.is_real_work is True
