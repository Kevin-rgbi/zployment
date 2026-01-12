def test_import_app_module():
    # Basic smoke test: module imports without error.
    import src.app  # noqa: F401


def test_import_home_page_module():
    # Basic smoke test: home page module imports and exposes expected function.
    from src.pages.home import display_home

    assert callable(display_home)