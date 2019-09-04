# Asteroid Tracker

Asteroid Tracker is a website which shows information about selected asteroids,
allows the public to schedule new observations and receive email alerts, and
creates timelapses from the observation data.

A [TOM Toolkit](https://tomtoolkit.github.io/) setup with the
[tom_education](https://github.com/joesingo/tom_education) plugin is used to
manage the data, and Asteroid Tracker is generated as a static site which uses
the `tom_education` APIs via JavaScript. The details of which asteroids to
include, URL of the TOM setup etc are defined in a YAML config file.

## Installation

* Install this package:
```
$ git clone <this repo>
$ pip install asteroid-tracker
```
* Set up a [tom_education](https://github.com/joesingo/tom_education) instance
  following the installation instructions
* Add `active` and `target_info` to `EXTRA_FIELDS` in `settings.py` in the
  Django app just created for `tom_education`
```python
EXTRA_FIELDS = [
    {'name': 'active', 'type': 'boolean'},
    {'name': 'target_info', 'type': 'string', 'hidden': True},
]
```

## Setup

Asteroids are defined as normal Target objects in the TOM. Two extra fields are
available
* `active`: Boolean field indicating whether new observation can be scheduled
  for this asteroid
* `target_info`: Markdown field for information about the asteroid. This
  forms the main content of the asteroid's page in Asteroid Tracker.
  [Showdown](https://github.com/showdownjs/showdown) is used for markdown: see
  its [syntax
  documentation](https://github.com/showdownjs/showdown/wiki/Showdown's-Markdown-syntax)
  for the precise flavour of markdown used.

For each asteroid created, make note of its *primary key*. This is the integer
shown as the final component in the URL on the Target view page.

To schedule observations without requiring the users to fill out the LCO
observation form, an [observation
template](https://github.com/joesingo/tom_education/blob/master/doc/templated_observation_forms.md)
is used for each asteroid. To create a template, click the 'LCO' button under
the 'Observe' tab in the Target view.

Once the asteroids have been set up, create a `config.yaml` file for Asteroid
Tracker. See the following example for the format and structure:
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

The `preview_image` field for each target is a (local) path to an image to be
used on the homepage of Asteroid Tracker. `teaser` is an optional short piece
of text which is also included on the homepage.

Asteroid tracker can now be created as a static website:
```
$ ast-tracker <path to config.yaml> <output dir>
```

This site can then be served with any web server. E.g. to use the built-in
Python HTTP server:
```
$ cd <output dir>
$ python3 -m http.server 5000
```

**Note:** Each preview image is copied at the time the site is exported.
Changes to the preview files (in their original locations) will have no affect
on the images in the exported site.

Most of the data stored in the TOM (asteroid name, `target_info`, template
parameters etc...) is not exported as part of the site (it is fetched at
`run-time' via JavaScript). This means that the site does not need to be
re-exported when these fields change.

The only exception is the `active` field; to update the active/past campaigns
on the homepage, the site must be re-exported.

### CORS headers

If serving Asteroid Tracker and the TOM from different hosts (including using
different ports on the same host), the TOM server will need to send the
appropriate [CORS](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing)
headers so that the browser will allow Ajax requests from Asteroid Tracker to
the TOM:

* Install `django-cors-headers`
```
$ pip install django-cors-headers
```
* Add `corsheaders` to `INSTALLED_APPS` in `settings.py`
* Add the `CorsMiddleware` in `MIDDLEWARE`
```python
MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]
```
* Set `CORS_ORIGIN_WHITELIST` to include the Asteroid Tracker host
* (alternatively, set `CORS_ORIGIN_ALLOW_ALL` to `True`). E.g:
```python
CORS_ORIGIN_WHITELIST = [
    'http://localhost:5000',
]
```

## Testing

The tests are written with
[pytest](https://docs.pytest.org/en/latest/index.html). Run `./run_tests.sh` to
run the tests and [Coverage.py](https://coverage.readthedocs.io/en/v4.5.x/).
