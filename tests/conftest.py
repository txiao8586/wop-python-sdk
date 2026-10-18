# -*- coding: utf-8 -*-
"""共享 fixture：黄金向量按 ref+sha256 从 wop-specs 真源拉取（对齐 java-sdk 模式）。

副本不落库：collect 阶段拉取并校验，mismatch 即失败（fail-closed）。
升级流程见 CONTRIBUTING：先合 wop-specs PR，再同步 WOP_SPECS_REF 与下方 sha256。
"""
import hashlib
import json
import os
import urllib.request

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))

WOP_SPECS_REF = "a1f7feb5b4af5c9052149e2adfd2063caa102677"
WOP_SPECS_SHA256 = {
    "crypto/crypto-vectors.json": "c7dd65740a1da9a5cfb804bca0c8b1bd7d4ab967adeb075297677a4bef148736",
    "interop/v1/interop-cases.json": "c920ca1a93ccb3899a659f59fed6ec4652cf9e1b3b58bbdac23c45ac3ed2353e",
}


def _fetch_pinned_specs():
    fixtures_dir = os.path.join(HERE, "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)  # 副本出库后目录可能不存在

    for src, expected in WOP_SPECS_SHA256.items():
        url = f"https://raw.githubusercontent.com/wop-platform/wop-specs/{WOP_SPECS_REF}/{src}"
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected:
            raise RuntimeError(
                f"wop-specs {src} sha256 mismatch：期望 {expected}，实得 {digest}；"
                "向量升级须先合 wop-specs PR 再同步钉版"
            )
        with open(os.path.join(HERE, "fixtures", os.path.basename(src)), "wb") as f:
            f.write(data)


_fetch_pinned_specs()

_VECTORS_PATH = os.path.join(HERE, "fixtures", "crypto-vectors.json")
with open(_VECTORS_PATH, "r", encoding="utf-8") as _f:
    VECTORS = json.load(_f)


@pytest.fixture(scope="session")
def vectors():
    return VECTORS


# ---------- formatRules 三件套哨兵（spec:A2）----------
# 已知 id 全集按消费端分域：header-* 由 test_digest 消费（check_digest_header 格式层），
# b64url-* 由 test_encoding 消费（b64url_decode）。真源向量增删/改名时，
# 两个消费端的"未知 id 哨兵 + 条数哨兵"都会先炸，强制测试侧显式接入（禁止静默跳过）。
HEADER_RULE_IDS = frozenset(
    {
        "header-rsa-ok",
        "header-sm2-ok",
        "header-crossfamily",
        "header-double-space",
        "header-uppercase-hex",
        "header-wrong-hex-len",
    }
)
B64URL_RULE_IDS = frozenset(
    {
        "b64url-with-padding",
        "b64url-illegal-char",
        "b64url-trailing-bits-noncanonical-2",
        "b64url-trailing-bits-canonical-2",
        "b64url-trailing-bits-noncanonical-3",
        "b64url-trailing-bits-canonical-3",
    }
)
ALL_FORMAT_RULE_IDS = HEADER_RULE_IDS | B64URL_RULE_IDS
FORMAT_RULES_COUNT = 12

@pytest.fixture(scope="session")
def vec_keys():
    return VECTORS["keys"]
