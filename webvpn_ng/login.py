from typing import Optional

import json
from functools import lru_cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .utils import get_cache_path

LOGIN_URL_1 = r"https://sso.buaa.edu.cn/login?service=https%3A%2F%2Fd.buaa.edu.cn%2Flogin%3Fcas_login%3Dtrue"
LOGIN_URL_2 = r"https://sso.buaa.edu.cn/login"


@lru_cache()
def get_cookie_cache_path() -> Path:
    return get_cache_path() / "cookie.json"


@lru_cache()
def get_user_cache_path() -> Path:
    return get_cache_path() / "user.json"


def login(username: str, password: str, token: str):
    sess = requests.Session()

    # Step 1: Get `execution` from login page
    rsp = sess.get(LOGIN_URL_1)
    soup = BeautifulSoup(rsp.content, "html.parser")
    tag = soup.find("input", {"name": "execution"})
    assert tag is not None
    execution = tag["value"]

    # Step 2: Post username and password
    data = {
        "username": username,
        "password": password,
        "submit": "登录",
        "type": "username_password",
        "execution": execution,
        "_eventId": "submit",
    }

    rsp = sess.post(LOGIN_URL_2, data=data)

    if rsp.ok:
        cookies = sess.cookies.get_dict()
        with open(get_cookie_cache_path(), "w") as f:
            json.dump(cookies, f)

        with open(get_user_cache_path(), "w") as f:
            json.dump({
                "username": username,
                "password": password,
                "token": token,
            }, f)

    return rsp.ok


def check_login() -> bool:
    if not get_cookie_cache_path().exists():
        return False

    with open(get_cookie_cache_path(), "r") as f:
        cookies = json.load(f)

    sess = requests.Session()
    sess.cookies.update(cookies)

    rsp = sess.get("https://d.buaa.edu.cn/", allow_redirects=False)

    if rsp.status_code == 200:
        return True

    if not get_user_cache_path().exists():
        return False

    with open(get_user_cache_path(), "r") as f:
        user = json.load(f)

    return login(user["username"], user["password"], user["token"])


def get_cookie() -> str:
    if not get_cookie_cache_path().exists():
        raise RuntimeError("Not logged in")

    with open(get_cookie_cache_path(), "r") as f:
        cookies = json.load(f)

    return "; ".join(f"{k}={v}" for k, v in cookies.items())


def get_token() -> str:
    if not get_user_cache_path().exists():
        raise RuntimeError("Not logged in")

    with open(get_user_cache_path(), "r") as f:
        user = json.load(f)

    return user["token"]


def get_server(token: str) -> Optional[str]:
    rsp = requests.get(
        "https://webvpn.sota.wiki/api/v1/server", params={"token": token}
    )
    data = rsp.json()

    if "server" not in data:
        return None

    return data["server"]
