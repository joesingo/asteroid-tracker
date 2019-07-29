from unittest.mock import patch

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
        {"tom_education_url": "hello", "targets": [{"pk": 1, "template": 3, "preview_image": "s"}]},
        {"tom_education_url": "hello", "targets": [{"pk": 1, "template": 3, "preview_image": "s",
                                                    "teaser": "hello"}]},
    ])
    def test_valid_configs(self, config, tmp_path):
        p = tmp_path / "c.yaml"
        p.write_text(yaml.dump(config))
        try:
            SiteBuilder.parse_config(p)
        except InvalidConfigError as ex:
            assert False, f"InvalidConfigError incorrectly raised: {ex}"

    def test_parse_config(self, tmp_path):
        p = tmp_path / "c.yaml"
        p.write_text(yaml.dump({
            "tom_education_url": "url",
            "targets": [{"pk": 1, "template": 3, "preview_image": "img"}]
        }))
        config = SiteBuilder.parse_config(p)
        assert config.tom_education_url == "url"
        assert config.targets == [Target(pk=1, template=3, preview_image="img")]

class TestSiteBuilder:
    @pytest.fixture
    def config(self):
        return Config(
            tom_education_url="someurl",
            targets=[dict(pk=1, template=1, preview_image="img", teaser="teaser")]
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
            assert excinfo.value == "Could not connect to TOM at 'somethingmadeup'"

    def test_get_pages(self, config):
        config.targets = [
            Target(pk=100, template=1, preview_image="img.png", teaser="hello"),
            Target(pk=101, template=1, preview_image="img.png"),
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
                            "name": "Cool target"
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
        assert pages[0].context["api_url"].endswith("/100/")
        assert pages[1].context["api_url"].endswith("/101/")
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
            }, {
                "url": "/target_2",
                "name": "Cool target",
                "image_name": "101.png",
                "teaser": "",
            }]
        }
