# Asteroid Tracker

**TODO:**
* Description of the project
* Explain `target_info` and markdown dialect
* Explain that active/past on homepage is determined when the site is exported

## Installation

* Install this package:
```
$ git clone <this repo>
$ pip install asteroid-tracker
```
* Set up a [tom_education](https://github.com/joesingo/tom_education) instance
* Add `active` and `target_info` to `EXTRA_FIELDS` in `settings.py` in the
  `tom_education` app
```python
EXTRA_FIELDS = [
    {'name': 'active', 'type': 'boolean'},
    {'name': 'target_info', 'type': 'string', 'hidden': True},
]
```
* Create targets and populate `target_info`. Check the `active` checkbox if the
  new observations should be allowed for the target
* Create an observation template for each target
* Create `config.yaml` with the following structure:
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
* Export your asteroid tracker instance as a static website:
```
$ ast-tracker <path to config.yaml> <output dir>
```
* (Optional) Serve the site with built-in Python HTTP server:
```
$ cd <output dir>
$ python3 -m http.server 5000
```

### CORS headers

If serving Asteroid Tracker and the `tom_education` site from different hosts
(including serving from different ports on the same host), the `tom_education`
server will need to send the appropriate
[CORS](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing) headers to
allow Ajax requests from the Asteroid Tracker site to work:

* Install `django-cors-headers`
```
$ pip install django-cors-headers
```
* Add `corsheaders` to `INSTALLED_APPS` in `settings.py`
* Set `CORS_ORIGIN_WHITELIST` in `settings.py` to include the Asteroid Tracker
host (alternatively, set `CORS_ORIGIN_ALLOW_ALL` to `True`). E.g:
```python
CORS_ORIGIN_WHITELIST = [
    'http://localhost:5000',
]
```

## Testing

The tests are written with
[pytest](https://docs.pytest.org/en/latest/index.html). Run `./run_tests.sh` to
run the tests and [Coverage.py](https://coverage.readthedocs.io/en/v4.5.x/).
