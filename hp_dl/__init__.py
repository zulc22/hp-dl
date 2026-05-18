from urllib.error import URLError
import requests
import time


def retry_until_no_error(f):
    def timeout():
        t = 2.5
        print("Retry in {}s".format(t))
        time.sleep(t)

    while True:
        try:
            return f()
        except ConnectionError as e:
            print("ConnectionError:", e.args)
            timeout()
        except URLError as e:
            print("URLError:", e.args)
            timeout()
        except requests.exceptions.ConnectionError as e:
            print("ConnectionError:", e.args)
            timeout()


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
