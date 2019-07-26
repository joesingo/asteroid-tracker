from dataclasses import dataclass
from datetime import datetime
import os.path
from pathlib import Path
import sys
import shutil

import yaml
from jinja2 import Environment, FileSystemLoader
import requests

def current_year():
    return datetime.now().strftime("%Y")

@dataclass
class Target:
    pk: int
    template: int

class SiteBuilder:
    def __init__(self, config_path):
        config = self.parse_config(config_path)
        self.base_url = config["tom_education_url"]
        self.targets = [Target(**info) for info in config["targets"]]

        # Remove trailing slash from base URL so that JS client can always
        # append API url to base without worrying about double /
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        # Construct Jinja environment
        here = Path(os.path.dirname(__file__))
        template_dir = here / "templates"
        self.static_dir = here / "static"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.env.globals["current_year"] = current_year()

    def parse_config(self, path):
        return yaml.safe_load(path.read_text())

    def build_site(self, outdir):
        outdir.mkdir(exist_ok=True)
        template = self.env.get_template("asteroid.html.tmpl")

        # Build a page for each target
        for target in self.targets:
            api_url = f"/api/target/{target.pk}/"
            response = requests.get(self.base_url + api_url)
            details = response.json()

            context = {
                "base_url": self.base_url,
                "api_url": api_url
            }

            identifier = details["target"]["identifier"]
            target_dir = outdir / identifier
            target_dir.mkdir(exist_ok=True)
            outfile = target_dir / "index.html"
            outfile.write_text(template.render(**context))

        # Copy static files
        out_static = outdir / "static"
        if out_static.exists():
            shutil.rmtree(out_static)
        shutil.copytree(self.static_dir, out_static)

def main():
    # TODO: use argparse or click or something...
    try:
        config_path = Path(sys.argv[1])
        out_path = Path(sys.argv[2])
    except IndexError:
        print("invalid usage", file=sys.stderr)
        sys.exit(1)

    builder = SiteBuilder(config_path)
    builder.build_site(out_path)

if __name__ == "__main__":
    main()
