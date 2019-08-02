import argparse
from dataclasses import dataclass
from datetime import datetime
import os.path
from pathlib import Path
import sys
import shutil
from typing import Dict, List

import yaml
import jinja2
import requests

from asteroid_tracker.exceptions import (
    AsteroidTrackerError,
    InvalidConfigError,
    TomConnectionError,
)

FACILITY = "LCO"

def current_year():
    return datetime.now().strftime("%Y")

@dataclass
class Target:
    pk: int
    template_name: str
    preview_image: str
    teaser: str = ""

    def preview_image_name(self):
        """
        Return the filename for the preview image to be copied to the static
        output directory
        """
        suffix = Path(self.preview_image).suffix
        return f"{self.pk}{suffix}"

@dataclass
class Config:
    tom_education_url: str
    targets: List[Target]

    def __init__(self, tom_education_url: str, targets: List[Dict]):
        self.tom_education_url = tom_education_url
        self.targets = [Target(**kw) for kw in targets]

@dataclass
class Page:
    name: str
    template: jinja2.Template
    context: dict

class SiteBuilder:
    def __init__(self, config):
        self.config = config
        self.base_url = config.tom_education_url

        # Remove trailing slash from base URL so that JS client can always
        # append API url to base without worrying about double /
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        # Construct Jinja environment
        here = Path(os.path.dirname(__file__))
        template_dir = here / "templates"
        self.static_dir = here / "static"
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        self.env.globals["current_year"] = current_year()

    @classmethod
    def parse_config(cls, path: Path) -> Config:
        config_dict = yaml.safe_load(path.read_text())
        try:
            return Config(**config_dict)
        except TypeError as ex:
            raise InvalidConfigError(f"Invalid config: {ex}")

    def build_site(self, outdir):
        outdir.mkdir(exist_ok=True)

        for page in self.get_pages():
            dest_dir = outdir / page.name
            dest_dir.mkdir(exist_ok=True)
            dest_file = dest_dir / "index.html"
            dest_file.write_text(page.template.render(**page.context))

        # Copy static files
        out_static = outdir / "static"
        if out_static.exists():
            shutil.rmtree(out_static)
        shutil.copytree(self.static_dir, out_static)
        # Copy target preview images
        preview_images = out_static / "previews"
        preview_images.mkdir(exist_ok=True)
        for target in self.config.targets:
            dest = preview_images / target.preview_image_name()
            shutil.copyfile(target.preview_image, dest)

    def get_pages(self):
        home_context = {"targets": []}

        # Create a page for each target
        target_template = self.env.get_template("asteroid.html.tmpl")
        for target in self.config.targets:
            api_url = f"/api/target/{target.pk}/"
            url = self.base_url + api_url
            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                raise TomConnectionError(f"Could not connect to TOM at '{url}'")
            details = response.json()

            identifier = details["target"]["identifier"]
            context = {
                "settings": {
                    "base_url": self.base_url,
                    "api_url": api_url,
                    "observe_api_url": "/api/observe/",
                    "target_pk": target.pk,
                    "template_name": target.template_name,
                    "facility": FACILITY,
                }
            }
            yield Page(name=identifier, template=target_template, context=context)

            # Add this target to the list to be shown on the home page
            home_context["targets"].append({
                "url": f"/{identifier}",
                "name": details["target"]["name"],
                "image_name": target.preview_image_name(),
                "teaser": target.teaser
            })

        # Home page
        yield Page(
            name="",
            template=self.env.get_template("home.html.tmpl"),
            context=home_context
        )

def main():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Create a static site to view and create timelapses of "
                    "asteroids using an instance of the TOM Toolkit"
    )
    parser.add_argument(
        "config",
        help="Path to YAML config file",
        type=Path
    )
    parser.add_argument(
        "output_directory",
        help="Directory to write static site to",
        type=Path
    )
    args = parser.parse_args(sys.argv[1:])
    try:
        config = SiteBuilder.parse_config(args.config)
        builder = SiteBuilder(config)
        builder.build_site(args.output_directory)
    except AsteroidTrackerError as ex:
        parser.error(ex)

if __name__ == "__main__":  # pragma: no cover
    main()
