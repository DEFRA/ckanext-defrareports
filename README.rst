====================
ckanext-defrareports
====================

**Status:** Development

**CKAN Version**: 2.6+

--------
Overview
--------

Pluggable ckan reporting extension enabling reporting on various metrics including:

* Publishing
* Dataset/resource access
* Broken resource links
* Various quality metrics
   * Readability of title/description
   * Resource links
      * Dead links
      * Duplicate links
   * Contact info present
   * Temporal data exists and is accurate (when necessary)
   * Has valid license
* System stats showing total counts of datasets...
   * Missing contact info
   * Missing maintainer info
   * Missing license info
   * Public vs private
   * Harvest source stats


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-defrareports:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-defrareports Python package into your virtual environment::

     pip install -e /path/to/ckanext-defrareports

3. Add ``defrareports`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


------------------------
Development Installation
------------------------

To install ckanext-defrareports for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/niross/ckanext-defrareports.git
    cd ckanext-defrareports
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.defrareports --cover-inclusive --cover-erase --cover-tests

