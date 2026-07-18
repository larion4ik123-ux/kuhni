from backend.app.providers.openai_compatible import OpenAICompatibleGenerationProvider


def test_polza_urls_do_not_duplicate_api_version() -> None:
    provider = OpenAICompatibleGenerationProvider
    assert provider._media_url("https://polza.ai/api/v1") == "https://polza.ai/api/v1/media"
    assert provider._images_url("https://polza.ai/api/v1") == "https://polza.ai/api/v2/images/generations"


def test_polza_urls_accept_origin_or_api_base() -> None:
    provider = OpenAICompatibleGenerationProvider
    assert provider._media_url("https://polza.ai") == "https://polza.ai/api/v1/media"
    assert provider._media_url("https://polza.ai/api") == "https://polza.ai/api/v1/media"
