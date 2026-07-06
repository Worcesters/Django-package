"""Mixin pytest/Django TestCase — active le mode strict via settings."""

from __future__ import annotations

from typing import Any


class PayloadSentinelTestMixin:
    """
    Mixin de test : active PAYLOAD_SENTINEL_STRICT_IN_TESTS pour la classe.

    Usage :
        class MyTests(PayloadSentinelTestMixin, TestCase):
            ...
    """

    @classmethod
    def setUpClass(cls) -> None:
        from django.test.utils import override_settings

        cls._strict_override = override_settings(PAYLOAD_SENTINEL_STRICT_IN_TESTS=True)
        cls._strict_override.enable()
        super().setUpClass()  # type: ignore[misc]

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()  # type: ignore[misc]
        cls._strict_override.disable()

    def run(self, result: Any) -> Any:
        return super().run(result)  # type: ignore[misc]
