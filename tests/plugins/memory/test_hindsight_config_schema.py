"""Tests for Hindsight's declared config surface."""

from pathlib import Path

import pytest

from plugins.memory.config_schema import (
    KIND_SECRET,
    KIND_SELECT,
    get_provider_config_schema,
)

_REPO_PLUGINS = Path(__file__).resolve().parents[3] / "plugins" / "memory"


@pytest.fixture(autouse=True)
def _point_discovery_at_repo_source(monkeypatch):
    """外置记忆 Provider 不内置：运行时只扫用户安装目录。schema 测试校验的是
    repo 源码里的声明文件，与发布包是否内置无关，直接把 find_provider_dir 指回
    repo 的 plugins/memory/。"""
    monkeypatch.setattr(
        "plugins.memory.find_provider_dir",
        lambda name: (_REPO_PLUGINS / name) if (_REPO_PLUGINS / name / "__init__.py").exists() else None,
    )


def test_hindsight_is_declared():
    provider = get_provider_config_schema("hindsight")

    assert provider is not None
    assert provider.label == "Hindsight"
    assert {field.key for field in provider.fields} == {
        "mode",
        "api_key",
        "api_url",
        "bank_id",
        "recall_budget",
    }


def test_fields_are_all_inline():
    provider = get_provider_config_schema("hindsight")
    assert provider is not None

    # Hindsight is simple enough to render fully in the compact panel, so it
    # never grows a Full config… modal.
    assert all(field.inline for field in provider.fields)


def test_mode_gating_is_expressed_as_select_options():
    provider = get_provider_config_schema("hindsight")
    assert provider is not None

    mode = next(field for field in provider.fields if field.key == "mode")
    assert mode.kind == KIND_SELECT
    assert mode.allowed_values() == {"cloud", "local_external"}
    # local_embedded is intentionally unsupported on desktop.
    assert "local_embedded" not in mode.allowed_values()


def test_api_key_is_a_secret_bound_to_env():
    provider = get_provider_config_schema("hindsight")
    assert provider is not None

    api_key = next(field for field in provider.fields if field.key == "api_key")
    assert api_key.kind == KIND_SECRET
    assert api_key.is_secret is True
    assert api_key.env_key == "HINDSIGHT_API_KEY"
