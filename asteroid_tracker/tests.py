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
