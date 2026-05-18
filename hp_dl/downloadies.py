# Source - https://stackoverflow.com/a/53877507
# Posted by Chris Chute
# Retrieved 2026-05-18, License - CC BY-SA 4.0

from hp_dl import retry_until_no_error
import requests
import os
import urllib.request

from tqdm import tqdm


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_path):
    if os.path.exists(output_path):
        print("File already exists:", output_path)
        print("Checking if correctly sized...")
        h = retry_until_no_error(lambda: requests.head(url).headers)
        if "content-length" not in h:
            print("HEAD request didn't tell us the file size. Redownloading.")
        else:
            if os.path.getsize(output_path) != int(h["content-length"]):
                print("Size check failed. Redownloading.")
            else:
                print("Size matched, skipping download")
                return

    print("=>| Downloading to", output_path)
    with DownloadProgressBar(
        unit="B", unit_scale=True, miniters=1, desc=url.split("/")[-1]
    ) as t:
        retry_until_no_error(
            lambda: urllib.request.urlretrieve(
                url, filename=output_path, reporthook=t.update_to
            )
        )
