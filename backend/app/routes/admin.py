"""Protected content-management UI and API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.deps import get_current_admin, get_templates
from backend.app.core.security import (
    create_csrf_token,
    create_session_token,
    validate_csrf_token,
    verify_password,
)
from backend.app.core.settings import get_settings
from backend.app.models import Admin, GalleryItem, MediaFile, Review, SiteBlock
from backend.app.services.media import store_uploaded_image

router = APIRouter()
db_dep = Annotated[AsyncSession, Depends(get_db)]
admin_dep = Annotated[Admin, Depends(get_current_admin)]


class BlockUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content: str | None = Field(default=None, max_length=5000)
    visible: bool = True


class GalleryUpdate(BaseModel):
    caption: str | None = Field(default=None, max_length=255)
    alt_text: str | None = Field(default=None, max_length=255)
    layout: str | None = Field(default=None, max_length=32)
    display_order: int = 0
    visible: bool = True


class ReviewUpdate(BaseModel):
    author_name: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=3000)
    rating: int = Field(default=5, ge=1, le=5)
    source_url: str | None = Field(default=None, max_length=512)
    display_order: int = 0
    visible: bool = True


def _require_csrf(token: str | None) -> None:
    if not token or not validate_csrf_token(token):
        raise HTTPException(status_code=403, detail="Недействительный CSRF-токен")


def _media_url(media: MediaFile | None) -> str | None:
    if not media:
        return None
    path = media.webp_path or media.jpg_path or media.stored_path
    return f"/media/{path.lstrip('/')}"


@router.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    return get_templates().TemplateResponse(
        request=request,
        name="admin/login.html",
        context={"csrf_token": create_csrf_token(), "error": None},
    )


@router.post("/admin/login", response_class=HTMLResponse)
async def login(
    request: Request,
    db: db_dep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    csrf_token: Annotated[str, Form()],
) -> HTMLResponse:
    if not validate_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Форма входа устарела")
    result = await db.execute(select(Admin).where(Admin.username == username.strip()))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_active or not verify_password(password, admin.password_hash):
        return get_templates().TemplateResponse(
            request=request,
            name="admin/login.html",
            context={
                "csrf_token": create_csrf_token(),
                "error": "Неверный логин или пароль",
            },
            status_code=401,
        )
    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie(
        "session",
        create_session_token({"admin_id": admin.id}),
        max_age=get_settings().ADMIN_SESSION_MAX_AGE_HOURS * 3600,
        httponly=True,
        secure=get_settings().APP_ENV == "production",
        samesite="lax",
    )
    return response


@router.post("/admin/logout")
async def logout() -> RedirectResponse:
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie("session")
    return response


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, admin: admin_dep) -> HTMLResponse:
    return get_templates().TemplateResponse(
        request=request,
        name="admin/index.html",
        context={"admin": admin, "csrf_token": create_csrf_token()},
    )


@router.get("/api/admin/content")
async def admin_content(db: db_dep, _admin: admin_dep) -> dict:
    blocks = (await db.execute(select(SiteBlock).order_by(SiteBlock.order))).scalars().all()
    gallery = (
        (await db.execute(select(GalleryItem).order_by(GalleryItem.display_order))).scalars().all()
    )
    reviews = (await db.execute(select(Review).order_by(Review.display_order))).scalars().all()
    media_ids = {
        item.media_file_id for item in [*blocks, *gallery] if item.media_file_id is not None
    }
    media = {}
    if media_ids:
        rows = (await db.execute(select(MediaFile).where(MediaFile.id.in_(media_ids)))).scalars()
        media = {item.id: item for item in rows}
    return {
        "blocks": [
            {
                "key": item.key,
                "title": item.title,
                "content": item.content,
                "visible": item.visible,
                "image_url": _media_url(media.get(item.media_file_id)),
            }
            for item in blocks
        ],
        "gallery": [
            {
                "id": item.id,
                "caption": item.caption,
                "alt_text": item.alt_text,
                "layout": item.layout,
                "display_order": item.display_order,
                "visible": item.visible,
                "image_url": _media_url(media.get(item.media_file_id)),
            }
            for item in gallery
        ],
        "reviews": [
            {
                "id": item.id,
                "author_name": item.author_name,
                "text": item.text,
                "rating": item.rating,
                "source_url": item.source_url,
                "display_order": item.display_order,
                "visible": item.visible,
            }
            for item in reviews
        ],
    }


@router.put("/api/admin/blocks/{key}")
async def update_block(
    key: str,
    payload: BlockUpdate,
    db: db_dep,
    _admin: admin_dep,
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> dict:
    _require_csrf(x_csrf_token)
    block = (await db.execute(select(SiteBlock).where(SiteBlock.key == key))).scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Блок не найден")
    block.title = payload.title
    block.content = payload.content
    block.visible = payload.visible
    await db.commit()
    return {"ok": True}


@router.post("/api/admin/blocks/{key}/image")
async def replace_block_image(
    key: str,
    db: db_dep,
    _admin: admin_dep,
    file: Annotated[UploadFile, File()],
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> dict:
    _require_csrf(x_csrf_token)
    block = (await db.execute(select(SiteBlock).where(SiteBlock.key == key))).scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Блок не найден")
    media = await store_uploaded_image(file, get_settings(), category="site")
    db.add(media)
    await db.flush()
    block.media_file_id = media.id
    await db.commit()
    return {"ok": True, "image_url": _media_url(media)}


@router.post("/api/admin/gallery")
async def create_gallery_item(
    db: db_dep,
    _admin: admin_dep,
    file: Annotated[UploadFile, File()],
    caption: Annotated[str, Form()],
    alt_text: Annotated[str, Form()] = "",
    layout: Annotated[str, Form()] = "",
    display_order: Annotated[int, Form()] = 0,
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> dict:
    _require_csrf(x_csrf_token)
    media = await store_uploaded_image(file, get_settings(), category="gallery", is_real_work=True)
    db.add(media)
    await db.flush()
    item = GalleryItem(
        media_file_id=media.id,
        caption=caption.strip(),
        alt_text=alt_text.strip() or caption.strip(),
        layout=layout.strip() or None,
        display_order=display_order,
        visible=True,
        is_real_work=True,
    )
    db.add(item)
    await db.commit()
    return {"ok": True, "id": item.id}


@router.put("/api/admin/gallery/{item_id}")
async def update_gallery_item(
    item_id: int,
    payload: GalleryUpdate,
    db: db_dep,
    _admin: admin_dep,
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> dict:
    _require_csrf(x_csrf_token)
    item = await db.get(GalleryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Работа не найдена")
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    await db.commit()
    return {"ok": True}


@router.post("/api/admin/gallery/{item_id}/image")
async def replace_gallery_image(
    item_id: int,
    db: db_dep,
    _admin: admin_dep,
    file: Annotated[UploadFile, File()],
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> dict:
    _require_csrf(x_csrf_token)
    item = await db.get(GalleryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Работа не найдена")
    media = await store_uploaded_image(file, get_settings(), category="gallery", is_real_work=True)
    db.add(media)
    await db.flush()
    item.media_file_id = media.id
    await db.commit()
    return {"ok": True, "image_url": _media_url(media)}


@router.delete("/api/admin/gallery/{item_id}")
async def delete_gallery_item(
    item_id: int,
    db: db_dep,
    _admin: admin_dep,
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> dict:
    _require_csrf(x_csrf_token)
    item = await db.get(GalleryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Работа не найдена")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.post("/api/admin/reviews")
async def create_review(
    payload: ReviewUpdate,
    db: db_dep,
    _admin: admin_dep,
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> dict:
    _require_csrf(x_csrf_token)
    item = Review(source="yandex", **payload.model_dump())
    db.add(item)
    await db.commit()
    return {"ok": True, "id": item.id}


@router.put("/api/admin/reviews/{item_id}")
async def update_review(
    item_id: int,
    payload: ReviewUpdate,
    db: db_dep,
    _admin: admin_dep,
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> dict:
    _require_csrf(x_csrf_token)
    item = await db.get(Review, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    await db.commit()
    return {"ok": True}


@router.delete("/api/admin/reviews/{item_id}")
async def delete_review(
    item_id: int,
    db: db_dep,
    _admin: admin_dep,
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    _require_csrf(x_csrf_token)
    item = await db.get(Review, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    await db.delete(item)
    await db.commit()
    return JSONResponse({"ok": True})
