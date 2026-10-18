# -*- coding: utf-8 -*-
"""stdlib urllib 适配器（零依赖，随主包交付）。"""
import urllib.error
import urllib.request
from typing import Dict, Iterator, Optional

from . import HttpResponse, _READ_CHUNK, read_capped
from ..config._models import HttpClientSettings


def _urllib_chunks(resp) -> Iterator[bytes]:
    """resp.read(n) 循环取块，直至 EOF；配合 read_capped 流式限量。"""
    while True:
        chunk = resp.read(_READ_CHUNK)
        if not chunk:
            break
        yield chunk


class UrllibTransport:
    """urllib.request 适配器；4xx/5xx 返回响应体而非抛异常（协议错误也在 body 里）。

    响应体按块流式读取并在累计超 MAX_RESPONSE_BYTES（11MB）时即刻中断。
    timeout_ms：读超时（毫秒），对齐配置模型 httpClient.readTimeoutMs；
    缺省取 HttpClientSettings.read_timeout（30s）——urlopen 缺省无超时可无限挂起。
    """

    def __init__(self, timeout_ms: int = HttpClientSettings.read_timeout) -> None:
        self._timeout_s = timeout_ms / 1000.0

    def send(
        self, method: str, url: str, headers: Dict[str, str], body: Optional[bytes]
    ) -> HttpResponse:
        req = urllib.request.Request(url, data=body, method=method)
        for name, value in headers.items():
            req.add_header(name, value)
        try:
            with urllib.request.urlopen(req, timeout=self._timeout_s) as resp:
                return HttpResponse(
                    resp.status,
                    {k.lower(): v for k, v in resp.headers.items()},
                    read_capped(_urllib_chunks(resp)),
                )
        except urllib.error.HTTPError as exc:
            return HttpResponse(
                exc.code,
                {k.lower(): v for k, v in exc.headers.items()},
                read_capped(_urllib_chunks(exc)),
            )
