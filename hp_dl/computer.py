from hp_dl import retry_until_no_error
from requests.sessions import Session


class Computer:
    def __init__(self, seriesID: str):
        self.seriesID = seriesID

        self.session = Session()
        self.session.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            + "AppleWebKit/537.36 (KHTML, like Gecko)"
            + "Chrome/146.0.0.0 Safari/537.36"
        )

        info = self._json_post(
            HPurl.specs(),
            {
                "cc": "us",
                "lc": "en",
                "utcOffset": "M0700",
                "captchaToken": "",
                "devices": [
                    {
                        "seriesOid": seriesID,
                        "modelOid": None,
                        "serialNumber": None,
                        "displayProductNumber": None,
                        "countryOfPurchase": "us",
                    }
                ],
            },
        )

        self.device_info = info["devices"][0]["productSpecs"]["data"]

        self.name = "{} ({})".format(
            self.device_info["productName"], self.device_info["productNumber"]
        )
        print("=> Got", self.name)

        info = self._json_get(HPurl.osVersionData(self.seriesID))

        platformList = info["osAvailablePlatformsAnsOS"]["osPlatforms"]
        self.platforms = [PlatformFamily(self, d) for d in platformList]
        self.platform_versions = [v for p in self.platforms for v in p.versions]

        print(
            " -> with",
            sum([len(p.versions) for p in self.platforms]),
            "supported operating systems:",
        )
        for f in self.platforms:
            print("  [{}]".format(f.name))
            for v in f.versions:
                print("    -", v.name)

    def drivers(self, os: "PlatformFamily | PlatformVersion"):
        print("=> Fetching drivers for", os.name)
        return self._json_post(
            HPurl.driverDetails(),
            {
                "cc": "us",
                "lc": "en",
                "osName": os.name,
                "osTMSId": os.id,
                "platformId": os.id if isinstance(os, PlatformFamily) else os.family.id,
                "productLineCode": self.device_info["productLineCode"],
                "productNumberOid": self.device_info["productNumberOid"],
                "productSeriesOid": self.device_info["productSeriesOid"],
            },
        )["softwareTypes"]

    def _json_get(self, url: str):
        res = retry_until_no_error(lambda: self.session.get(url))
        data = res.json()
        if "statusCode" in data and "code" not in data:
            data["code"] = data["statusCode"]
        if data["code"] != 200:
            raise Exception(data)
        return data["data"]

    def _json_post(self, url: str, jason):
        res = retry_until_no_error(lambda: self.session.post(url, json=jason))
        data = res.json()
        if "statusCode" in data and "code" not in data:
            data["code"] = data["statusCode"]
        if data["code"] != 200:
            raise Exception(data)
        return data["data"]

    def __repr__(self):
        return "<Computer '{}' (oid={})>".format(self.name, self.seriesID)


class PlatformFamily:
    def __init__(self, parent, data):
        self.parent: Computer = parent
        self.name: str = data["name"]
        self.id: str = data["id"]
        self.versions = [PlatformVersion(self, d) for d in data["osVersions"]]

    def __repr__(self):
        return "<PlatformFamily '{}' (id={})>".format(self.name, self.id)


class PlatformVersion:
    def __init__(self, parent, data):
        self.family: PlatformFamily = parent
        self.id: str = data["id"]
        self.name: str = data["name"]

    def __repr__(self):
        return "<PlatformVersion '{}' (id={})>".format(self.name, self.id)


class Driver:
    def __init__(self, data):
        self.original_meta = data
        self.name = data["title"]
        self.version = data["version"]
        self.url = data["fileUrl"]


class HPurl:
    WCC_SERVICES = "https://support.hp.com/wcc-services"
    ATTRIBUTES = "/pdp/attributes/us-en?oid={}&authState=anonymous&template=SWDSeriesDownload_nodriver"
    SPECS = "/profile/devices/warranty/specs?cache=true&authState=anonymous&template=SWDSeriesDownload_nodriver"
    OS_VERSION_DATA = "/swd-v2/osVersionData?cc=us&lc=en&productOid={}&authState=anonymous&template=SWDSeriesDownload_nodriver"
    DRIVER_DETAILS = (
        "/swd-v2/driverDetails?authState=anonymous&template=SWDSeriesDownload_nodriver"
    )

    @classmethod
    def attributes(cls, seriesID: str) -> str:
        return cls.WCC_SERVICES + cls.ATTRIBUTES.format(seriesID)

    @classmethod
    def specs(cls) -> str:
        return cls.WCC_SERVICES + cls.SPECS

    @classmethod
    def osVersionData(cls, seriesID: str) -> str:
        return cls.WCC_SERVICES + cls.OS_VERSION_DATA.format(seriesID)

    @classmethod
    def driverDetails(cls) -> str:
        return cls.WCC_SERVICES + cls.DRIVER_DETAILS
