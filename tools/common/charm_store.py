#!/usr/bin/python3

import logging
from pprint import pprint
import urllib3
import yaml

VERSION = 'v5'
API_URL = "https://api.jujucharms.com/{}/{}/{}/meta/id-revision"
API_URL = "https://api.jujucharms.com/charmstore/{}/{}/{}/meta/{}"


def cs_query(charm, series, uri='meta'):
    """ Query the charm store

    :param: charm: Name of charm in the charms store
    :param: series: Series of the charm in the charms store
    :param: uri: meta returns the following which can be addressed directly:
        ['archive-size',
         'archive-upload-time',
         'bundle-machine-count',
         'bundle-metadata',
         'bundle-unit-count',
         'bundles-containing',
         'can-ingest',
         'charm-actions',
         'charm-config',
         'charm-metadata',
         'charm-metrics',
         'charm-related',
         'common-info',
         'extra-info',
         'hash',
         'hash256',
         'id',
         'id-name',
         'id-revision',
         'id-series',
         'id-user',
         'manifest',
         'owner',
         'perm',
         'promulgated',
         'published',
         'resources',
         'revision-info',
         'stats',
         'supported-series',
         'tags',
         'terms']
    """
    url = API_URL.format(VERSION, series, charm, uri)
    http = urllib3.PoolManager()
    result = http.request('GET', url)
    if result.status == 200:
        return yaml.load(result.data)
    else:
        logging.error("FAILED to query: charm: {}, series {}, uri: {}, result:{}".format(charm, series, uri, result.status))


if __name__ == "__main__":
    pprint(cs_query('neutron-api', 'xenial', uri='charm-metadata'))
