import pytest
import yaml

from asteroid_tracker import (
    Config,
    SiteBuilder,
    Target,
)

class TestConfig:
    # Test invalid configs
    @pytest.mark.parametrize("config", [
        {"targets": []},
        {"tom_education_url": "blah"},
        {"tom_education_url": "blah", "targets": ["hello"]},
    ])
    def test_invalid_configs(self, config):
        with pytest.raises(TypeError):
            Config(**config)

    # Test valid configs
    @pytest.mark.parametrize("config", [
        {"tom_education_url": "hello", "targets": []},
        {"tom_education_url": "hello", "targets": [{"pk": 1, "template": 3, "preview_image": "s"}]},
        {"tom_education_url": "hello", "targets": [{"pk": 1, "template": 3, "preview_image": "s",
                                                    "teaser": "hello"}]},
    ])
    def test_valid_configs(self, config):
        try:
            Config(**config)
        except TypeError as ex:
            assert False, f"TypeError incorrectly raised: {ex}"

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

    def test_url_trailing_slash(self, config):
        # Trailing slash should be removed
        config.tom_education_url = "http://slash.net/"
        builder1 = SiteBuilder(config)
        assert builder1.base_url == "http://slash.net"
        # ... but only if present
        config.tom_education_url = "http://noslash.net"
        builder2 = SiteBuilder(config)
        assert builder2.base_url == "http://noslash.net"
