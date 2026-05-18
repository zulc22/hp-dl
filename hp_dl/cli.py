import datetime as dt
import os
from hp_dl.downloadies import download_url
import pathlib
import click
from hp_dl import computer, safe_filename
import json


@click.command()
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(False, False, True, True, path_type=pathlib.Path),
)
@click.option("--include-out-of-date", "-O", is_flag=True)
@click.argument("computer_id")
def main(
    output_dir: "pathlib.Path | None", include_out_of_date: bool, computer_id: str
):
    """
    Download an archive of all drivers for an HP computer.

    <computer_id> shows up at the end of the support URLs on HP's website,
    e.g. the 4065899 in the URL 'https://support.hp.com/us-en/product/details/hp-compaq-8000-elite-ultra-slim-pc/4065899'.
    """
    if output_dir is not None:
        output_dir.mkdir(exist_ok=True)

    print("Attempting to dump drivers for series", computer_id)
    c = computer.Computer(computer_id)

    if output_dir is None:
        output_dir = pathlib.Path("./" + safe_filename(c.name))
        print("Output path named automatically:", output_dir)
        output_dir.mkdir(exist_ok=True)

    for v in c.platform_versions:
        os_dump_path = output_dir / v.name
        os_dump_path.mkdir(exist_ok=True)
        for category in c.drivers(v):
            category_dump_path = os_dump_path / category["accordionName"]
            for driver in category["softwareDriversList"]:
                if driver["latestVersionDriver"] is not None:
                    download_driver(driver["latestVersionDriver"], category_dump_path)
                if include_out_of_date:
                    if driver["previousVersionOfDriversList"] is not None:
                        for d in driver["previousVersionOfDriversList"]:
                            download_driver(d, category_dump_path / "Previous versions")


def download_driver(data, directory: pathlib.Path):
    directory.mkdir(exist_ok=True)

    if data["detailInformation"]["fileName"] is None:
        print("Driver", data["title"], "is probably a link. skipping")
        return

    original_filename = pathlib.Path(data["detailInformation"]["fileName"])
    new_filename: str = safe_filename(
        original_filename.stem + " - " + data["title"] + original_filename.suffix
    )
    new_metafile: str = safe_filename(
        original_filename.stem + " - " + data["title"] + ".meta.json"
    )
    output_path = directory / new_filename
    with open(directory / new_metafile, "w") as fp:
        json.dump(data, fp)
    download_url(data["fileUrl"], str(output_path))
    try:
        updated_ts = dt.datetime.fromisoformat(data["versionUpdatedDate"]).timestamp()
        os.utime(output_path, (updated_ts, updated_ts))
    except Exception:
        print("Failed to set modified date, continuing")


if __name__ == "__main__":
    main()
