from bot.handlers.max_funnel import MaxFunnelHandler


def test_contact_and_image_are_extracted_from_max_attachments() -> None:
    phone = MaxFunnelHandler._extract_phone(
        "",
        [{"type": "contact", "payload": {"max_info": {"phone": "+7 910 000-00-00"}}}],
    )
    image = MaxFunnelHandler._extract_image_url(
        [{"type": "image", "payload": {"photos": {"small": "https://a/s", "large": "https://a/l"}}}]
    )
    assert phone == "+7 910 000-00-00"
    assert image == "https://a/l"


def test_fallback_target_is_a_max_user_not_chat() -> None:
    assert MaxFunnelHandler._chat_id({}, "777") == "user:777"
