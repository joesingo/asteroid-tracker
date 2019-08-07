from unittest.mock import patch

import jinja2
import pytest
import yaml

from asteroid_tracker import (
    InvalidConfigError,
    Config,
    Page,
    SiteBuilder,
    Target,
    TomConnectionError
)

class TestConfig:
    # Test invalid configs
    @pytest.mark.parametrize("config", [
        {"targets": []},
        {"tom_education_url": "blah"},
        {"tom_education_url": "blah", "targets": ["hello"]},
    ])
    def test_invalid_configs(self, config, tmp_path):
        p = tmp_path / "c.yaml"
        p.write_text(yaml.dump(config))
        with pytest.raises(InvalidConfigError):
            SiteBuilder.parse_config(p)

    # Test valid configs
    @pytest.mark.parametrize("config", [
        {"tom_education_url": "hello", "targets": []},
        {"tom_education_url": "hello", "targets": [{"pk": 1, "template_name": "t", "preview_image": "s"}]},
        {"tom_education_url": "hello", "targets": [{"pk": 1, "template_name": "t", "preview_image": "s",
                                                    "teaser": "hello"}]},
    ])
    def test_valid_configs(self, config, tmp_path):
        p = tmp_path / "c.yaml"
        p.write_text(yaml.dump(config))
        try:
            SiteBuilder.parse_config(p)
        except InvalidConfigError as ex:  # pragma: no cover
            assert False, f"InvalidConfigError incorrectly raised: {ex}"

    def test_parse_config(self, tmp_path):
        p = tmp_path / "c.yaml"
        p.write_text(yaml.dump({
            "tom_education_url": "url",
            "targets": [{"pk": 1, "template_name": "t", "preview_image": "img"}]
        }))
        config = SiteBuilder.parse_config(p)
        assert config.tom_education_url == "url"
        assert config.targets == [Target(pk=1, template_name="t", preview_image="img")]

class TestSiteBuilder:
    @pytest.fixture
    def config(self):
        return Config(
            tom_education_url="someurl",
            targets=[dict(pk=1, template_name="t", preview_image="img", teaser="teaser")]
        )

    @pytest.fixture
    def builder(self, config):
        return SiteBuilder(config)

    def test_url_trailing_slash(self, config):
        # Trailing slash should be removed
        config.tom_education_url = "http://slash.net/"
        builder1 = SiteBuilder(config)
        assert builder1.base_url == "http://slash.net"
        # ... but only if present
        config.tom_education_url = "http://noslash.net"
        builder2 = SiteBuilder(config)
        assert builder2.base_url == "http://noslash.net"

    def test_could_not_connect_to_tom(self, config, tmp_path):
        config.tom_education_url = "http://somethingmadeup"
        builder = SiteBuilder(config)
        with pytest.raises(TomConnectionError) as excinfo:
            builder.build_site(tmp_path)
        assert "Could not connect to TOM at 'http://somethingmadeup" in str(excinfo.value)

    def test_get_pages(self, config):
        config.targets = [
            Target(pk=100, template_name="t", preview_image="img.png", teaser="hello"),
            Target(pk=101, template_name="t", preview_image="img.png"),
        ]
        builder = SiteBuilder(config)

        with patch("asteroid_tracker.build_site.requests") as mock:
            class FakeResponse:
                times_called = 0
                def json(self):
                    self.times_called += 1
                    return {
                        "target": {
                            "identifier": f"target_{self.times_called}",
                            "name": "Cool target",
                            "extra_fields": {"active": False},
                        }
                    }

            mock.get.return_value = FakeResponse()
            pages = list(builder.get_pages())

        assert len(pages) == 3
        # Check names
        assert pages[0].name == "target_1"
        assert pages[1].name == "target_2"
        assert pages[2].name == ""  # home page
        # Check API URLs in context
        assert "settings" in pages[0].context
        assert set(pages[0].context["settings"].keys()) == {
            "api_url", "facility", "target_pk", "template_name", "base_url",
            "observe_api_url"
        }
        assert pages[0].context["settings"]["api_url"].endswith("/100/")
        assert pages[1].context["settings"]["api_url"].endswith("/101/")
        # Check templates
        assert pages[0].template == pages[1].template
        assert pages[0].template != pages[2].template
        # Check home page context
        assert pages[2].context == {
            "targets": [{
                "url": "/target_1",
                "name": "Cool target",
                "image_name": "100.png",
                "teaser": "hello",
                "active": False,
            }, {
                "url": "/target_2",
                "name": "Cool target",
                "image_name": "101.png",
                "teaser": "",
                "active": False,
            }]
        }

    def test_build_site(self, config, tmp_path):
        config.targets = []
        builder = SiteBuilder(config)

        template = jinja2.Template("{{ var }}")
        with patch("asteroid_tracker.build_site.SiteBuilder.get_pages") as mock:
            mock.return_value = [
                Page(name="", template=template, context={"var": "home page"}),
                Page(name="mypage", template=template, context={"var": "hello"}),
            ]
            builder.build_site(tmp_path)

        home = tmp_path / "index.html"
        assert home.exists()
        assert home.read_text() == "home page"

        page = tmp_path / "mypage" / "index.html"
        assert page.exists()
        assert page.read_text() == "hello"

    def test_copy_static_files(self, config, tmp_path):
        # Make some test static files
        in_static = tmp_path / "static"
        in_static.mkdir()
        (in_static / "somefile.txt").write_text("hello")
        subdir = in_static / "dir"
        subdir.mkdir()
        (subdir / "anotherfile.csv").write_text("csv here")
        # Make 'image' file for target preview
        img_dir = tmp_path / "images"
        img_dir.mkdir()
        img = img_dir / "asteroid.jpg"
        img.write_text("this is totally a JPEG")
        config.targets = [Target(pk=42, template_name="t", preview_image=str(img))]

        builder = SiteBuilder(config)
        outdir = tmp_path / "out"
        outdir.mkdir()
        # Override builder's static dir
        builder.static_dir = in_static

        with patch("asteroid_tracker.build_site.SiteBuilder.get_pages", return_value=[]):
            builder.build_site(outdir)

        out_static = outdir / "static"
        assert out_static.exists()

        txt_file = out_static / "somefile.txt"
        assert txt_file.exists()
        assert txt_file.read_text() == "hello"

        out_subdir = out_static / "dir"
        assert out_static.exists()
        csv_file = out_subdir / "anotherfile.csv"
        assert csv_file.exists()
        assert csv_file.read_text() == "csv here"

        out_images = out_static / "previews"
        assert out_images.exists()
        out_preview = out_images / "42.jpg"
        assert out_preview.exists()
        assert out_preview.read_text() == "this is totally a JPEG"

    def test_static_dir_already_exist(self, builder, tmp_path):
        # Make static dir with a file already in it
        outdir = tmp_path / "out"
        outdir.mkdir()
        static = outdir / "static"
        static.mkdir()
        (static / "sneakyfile.txt").write_text("this should be deleted")

        builder.config.targets = []
        with patch("asteroid_tracker.build_site.SiteBuilder.get_pages", return_value=[]):
            builder.build_site(outdir)

        assert static.exists()
        assert not (static / "sneakyfile.txt").exists()
