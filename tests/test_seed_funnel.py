from backend.app.seed import FUNNEL_QUESTIONS


def test_max_funnel_matches_the_customer_journey() -> None:
    keys = [item["key"] for item in sorted(FUNNEL_QUESTIONS, key=lambda item: item["order"])]

    assert keys == [
        "form",
        "width",
        "height",
        "area",
        "style",
        "color",
        "handle",
        "countertop",
        "appliances",
        "room_type",
        "photo",
        "wishes",
        "contact",
    ]
    assert "deadline" not in keys
    assert "confirmation" not in keys
