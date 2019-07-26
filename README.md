# Asteroid Tracker

**TODO:** description

## Installation

* Set up a tom_education instance
* Add `html_info` to `EXTRA_FIELDS` in `settings.py`
```python
EXTRA_FIELDS = [
    {'name': 'html_info', 'type': 'string'}
]
```
* Create targets and populate `html_info` in tags section
* Create an observation template for each target
* Create `config.yaml` as follows (change the target and template PKs as
  appropriate):
```yaml
tom_education_url: "http://localhost:8000",
targets:
  - pk: 1
    template: 1

  - pk: 2
    template: 1
```
* Set `CORS_ORIGIN_WHITELIST` in `settings.py` to include the host from which
  Asteroid Tracker will be hosted (alternatively, set `CORS_ORIGIN_ALLOW_ALL`
  to `True`):
```python
CORS_ORIGIN_WHITELIST = [
    'http://localhost:5000',
]
```
* Export your asteroid tracker instance as a static website:
```
$ asteroid-tracker <path to config.yaml> <output dir>
```
* (Optional) Serve the site with built-in Python HTTP server:
```
$ cd <output dir>
$ python3 -m http.server
```
