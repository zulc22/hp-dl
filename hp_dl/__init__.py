import requests
import time


def retry_until_no_error(f):
    while True:
        try:
            return f()
        except ConnectionError as e:
            print("ConnectionError:", e.args)
            print("Retry in 5s")
            time.sleep(5)
        except requests.exceptions.ConnectionError as e:
            print("ConnectionError:", e.args)
            print("Retry in 5s")
            time.sleep(5)


def safe_filename(n: str) -> str:
    return (
        n.replace("/", "⧸")
        .replace("<", "＜")
        .replace(">", "＞")
        .replace(":", "﹕")
        .replace('"', "”")
        .replace("\\", "⧵")
        .replace("|", "│")
        .replace("?", "﹖")
        .replace("*", "∗")
    )
