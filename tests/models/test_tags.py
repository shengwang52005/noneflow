# type: ignore
import json
from collections import OrderedDict

import pytest
from github.Issue import Issue
from pydantic import ValidationError
from pytest_mock import MockerFixture

from src.models import AdapterPublishInfo, MyValidationError


def generate_issue_body(
    name: str = "name",
    desc: str = "desc",
    module_name: str = "module_name",
    project_link: str = "project_link",
    homepage: str = "https://v2.nonebot.dev",
    tags: list = [{"label": "test", "color": "#ffffff"}],
):
    return f"""**协议名称：**\n\n{name}\n\n**协议功能：**\n\n{desc}\n\n**PyPI 项目名：**\n\n{project_link}\n\n**协议 import 包名：**\n\n{module_name}\n\n**协议项目仓库/主页链接：**\n\n{homepage}\n\n**标签：**\n\n{json.dumps(tags)}"""


def mocked_requests_get(url: str):
    class MockResponse:
        def __init__(self, status_code: int):
            self.status_code = status_code

    if url == "https://pypi.org/pypi/project_link/json":
        return MockResponse(200)
    if url == "https://v2.nonebot.dev":
        return MockResponse(200)

    return MockResponse(404)


def test_adapter_tags_color_invalid(mocker: MockerFixture) -> None:
    """测试标签颜色不正确的情况"""
    mock_requests = mocker.patch("requests.get", side_effect=mocked_requests_get)

    with pytest.raises(ValidationError) as e:
        info = AdapterPublishInfo(
            module_name="module_name",
            project_link="project_link",
            name="name",
            desc="desc",
            author="author",
            homepage="https://v2.nonebot.dev",
            tags=json.dumps([{"label": "test", "color": "#adbcdef"}]),
            is_official=False,
        )
    assert "标签颜色不符合十六进制颜色码规则" in str(e.value)


def test_adapter_tags_label_invalid(mocker: MockerFixture) -> None:
    """测试标签名称不正确的情况"""
    mock_requests = mocker.patch("requests.get", side_effect=mocked_requests_get)

    with pytest.raises(ValidationError) as e:
        info = AdapterPublishInfo(
            module_name="module_name",
            project_link="project_link",
            name="name",
            desc="desc",
            author="author",
            homepage="https://v2.nonebot.dev",
            tags=json.dumps([{"label": "12345678901", "color": "#adbcde"}]),
            is_official=False,
        )
    assert "标签名称不能超过 10 个字符" in str(e.value)


def test_adapter_tags_number_invalid(mocker: MockerFixture) -> None:
    """测试标签数量不正确的情况"""
    mock_requests = mocker.patch("requests.get", side_effect=mocked_requests_get)

    with pytest.raises(ValidationError) as e:
        info = AdapterPublishInfo(
            module_name="module_name",
            project_link="project_link",
            name="name",
            desc="desc",
            author="author",
            homepage="https://v2.nonebot.dev",
            tags=json.dumps(
                [
                    {"label": "1", "color": "#ffffff"},
                    {"label": "2", "color": "#ffffff"},
                    {"label": "3", "color": "#ffffff"},
                    {"label": "4", "color": "#ffffff"},
                ]
            ),
            is_official=False,
        )
    assert "标签数量不能超过 3 个" in str(e.value)


def test_adapter_tags_json_invalid(mocker: MockerFixture) -> None:
    """测试标签 json 格式不正确的情况"""
    mock_requests = mocker.patch("requests.get", side_effect=mocked_requests_get)

    with pytest.raises(ValidationError) as e:
        info = AdapterPublishInfo(
            module_name="module_name",
            project_link="project_link",
            name="name",
            desc="desc",
            author="author",
            homepage="https://v2.nonebot.dev",
            tags=json.dumps([{"label": "1", "color": "#ffffff"}]) + "1",
            is_official=False,
        )
    assert "标签不符合 JSON 格式" in str(e.value)
