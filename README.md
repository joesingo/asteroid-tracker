# Asteroid Tracker

**TODO:** description

## Installation

* Install this package:
```
$ git clone <this repo>
$ pip install asteroid-tracker
```
* Set up a [tom_education](https://github.com/joesingo/tom_education) instance
* Add `target_info` to `EXTRA_FIELDS` in `settings.py`
```python
EXTRA_FIELDS = [
    {'name': 'target_info', 'type': 'string'}
]
```
* Create targets and populate `target_info` in tags section
* Create an observation template for each target
* Create `config.yaml` as follows (change the target and template names as
  appropriate):
```yaml
tom_education_url: "http://localhost:8000",
targets:
  - pk: 1
    template_name: mytemplate
    preview_image: /path/to/image.png
    teaser: This text is shown on the homepage

  - pk: 2
    template_name: another-template
    preview_image: /path/to/another/image.png
```
* If serving Asteroid Tracker and the `tom_education` site from different hosts,
  set `CORS_ORIGIN_WHITELIST` in `settings.py` to include the Asteroid Tracker
  host (alternatively, set `CORS_ORIGIN_ALLOW_ALL` to `True`). E.g:
```python
CORS_ORIGIN_WHITELIST = [
    'http://localhost:5000',
]
```
* Export your asteroid tracker instance as a static website:
```
$ ast-tracker <path to config.yaml> <output dir>
```
* (Optional) Serve the site with built-in Python HTTP server:
```
$ cd <output dir>
$ python3 -m http.server
```

## Testing

The tests are written with
[pytest](https://docs.pytest.org/en/latest/index.html). Run `./run_tests.sh` to
run the tests and [Coverage.py](https://coverage.readthedocs.io/en/v4.5.x/).
