"""测试共享 helper（独立模块：test 模块间禁止互相 import，Sourcery dont-import-test-modules）。"""
import json
from pathlib import Path

RSA_REQ = "WOP-RSA3072-SHA256"


def _valid_config_dict(vec_keys) -> dict:
    return {
        "appKey": "app_10012481831",
        "suite": RSA_REQ,
        "merchantPrivateKey": vec_keys["rsa3072"]["privatePkcs8B64"],
        "platformPublicKey": vec_keys["rsa3072"]["publicSpkiB64"],
        "serverRoot": "https://gw.example.com/gateway",
        "backupServerRoots": ["https://gw-backup.example.com/gateway"],
        "expiredSeconds": 1800,
        "httpClient": {
            "connectTimeout": 10000,
            "readTimeout": 30000,
            "maxRetryCount": 3,
        },
    }


def _write_config(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
