#!/usr/bin/python

import logging
import yaml
import common.control_data_common as control_data


class InvalidSource(Exception):
    pass


class Charm(object):

    def __init__(self, name, charm_dict={}):
        self.name = name
        self.series = None
        # Defaults
        self.source = 'stable'
        self.url = 'cs:{}'.format(self.name)
        self.custom_url = False
        self.num_units = 1
        self.options = {}
        self.constraints = None
        self.origin = None
        self.SUPPORTED_SOURCES = ['stable', 'next', 'github']
        self.OPENSTACK_PROJECT = 'openstack'
        self.OPENSTACK_CHARM_PREFIX = 'charm-'
        self.OPENSTACK_CHARMERS_USER = 'openstack-charmers'
        self.OPENSTACK_CHARMERS_NEXT_USER = 'openstack-charmers-next'

        if charm_dict:
            self._load_from_dict(charm_dict)

    def __str__(self):
        return 'Charm Object: {}'.format(self.name)

    def _load_from_dict(self, charm_dict, update=False):
        # TODO: handle yaml charm urls
        # This uses the hammer custom_url which would be nice to keep for
        # overrides only like mongodb
        print("CHARM_DICT:", charm_dict)
        if charm_dict[self.name].get('charm'):
            logging.warn("Overriding charm url to {}. This may not be the "
                         "expected result. Run charm.set_url() to configure "
                         "expected url."
                         "".format(charm_dict[self.name].get('charm')))
            self.set_url(charm_dict[self.name].get('charm'), custom_url=True)
        if charm_dict[self.name].get('num_units'):
            self.set_num_units(charm_dict[self.name].get('num_units'))
        if charm_dict[self.name].get('options'):
            if update:
                self.update_options(**charm_dict[self.name].get('options'))
            else:
                self.set_options(**charm_dict[self.name].get('options'))
        if charm_dict[self.name].get('to'):
            self.set_placement([charm_dict[self.name].get('to')])
        if charm_dict[self.name].get('constraints'):
            self.set_constraints([charm_dict[self.name].get('constraints')])

    def _load_from_yaml(self):
        # TODO
        pass

    def update_charm(self, charm_dict):
        self._load_from_dict(charm_dict, update=True)

    def get_dict(self):
        charm_attr_dict = {'charm': self.get_url(),
                           'num_units': self.get_num_units()}
        if self.get_series():
            charm_attr_dict['series'] = self.get_series()
        if self.get_options():
            charm_attr_dict['options'] = self.get_options()
        if self.get_placement():
            charm_attr_dict['to'] = self.get_options()

        return {self.name: charm_attr_dict}

    def get_yaml(self):
        return yaml.dump(self.get_dict())

    def set_url(self, source='stable', series=None, proto='cs:', user=None,
                branch=None, custom_url=False):
        """
        """
        if custom_url:
            self.url = source
            self.custom_url = True
            return

        if (not source == self.name and
                source not in self.SUPPORTED_SOURCES):
            raise InvalidSource("{} is not a valid source. Valid sources are: "
                                "stable, next or github".format(source))

        if source == 'github':
            if user:
                self.url = "git://github.com/{}/{}{}".format(
                        user,
                        self.OPENSTACK_CHARM_PREFIX,
                        self.name)
            else:
                self.url = "git://github.com/{}/{}{}".format(
                        self.OPENSTACK_PROJECT,
                        self.OPENSTACK_CHARM_PREFIX,
                        self.name)
            return

        charmstore_url = []

        if 'next' in source:
            user = self.OPENSTACK_CHARMERS_NEXT_USER
        if user:
            user = '~{}'.format(user)
            charmstore_url.append(user)

        # Series specific
        if series:
            self.set_series(series)
        if self.get_series():
            series = self.get_series()
            charmstore_url.append(series)

        charmstore_url.append(self.name)

        self.url = "{}{}".format(proto, "/".join(charmstore_url))

    def set_origin(self, target, option='openstack-origin',
                   custom_origin=False):
        origin = None
        series = None
        release = None
        pocket = None
        # If custom set it directly
        if custom_origin:
            self.origin = target
            return
        splits = target.split('-')
        if len(splits) == 2:
            series, release = splits
        elif len(splits) == 3:
            series, release, pocket = splits
        # Do not set origin if the release is native to the series
        if (not pocket and
                series in control_data.NATIVE_RELEASES.keys() and
                release == control_data.NATIVE_RELEASES[series]):
            logging.debug("{} is native to {}. Not setting origin."
                          "".format(release, series))
            self.origin = None
            return

        origin = 'cloud:{}-{}'.format(series, release)
        if pocket:
            origin = '{}/{}'.format(origin, pocket)

        self.origin = origin
        if (self.name in control_data.CHARMS_USE_ORIGIN or
                control_data.SERVICE_TO_CHARM.get(self.name) in
                control_data.CHARMS_USE_ORIGIN):
            logging.debug("Use openstack-origin: {} for {}"
                          "".format(self.origin, self.name))
            self.update_options(**{'opentstack-origin': self.origin})
        elif (self.name in control_data.CHARMS_USE_SOURCE or
                control_data.SERVICE_TO_CHARM.get(self.name) in
                control_data.CHARMS_USE_SOURCE):
            logging.debug("Use source: {} for {}"
                          "".format(self.origin, self.name))
            self.update_options(**{'source': self.origin})
        else:
            logging.warn("{} not in CHARMS_USE_ORIGIN or CHARMS_USE_SOURCE"
                         "".format(self.name))

    def get_origin(self):
        return self.origin

    def get_url(self):
        return self.url

    def get_source(self):
        return self.source

    def set_num_units(self, num_units):
        self.num_units = num_units

    def get_num_units(self):
        return self.num_units

    def get_options(self):
        return self.options

    def set_options(self, **kwargs):
        options = {}
        for key, val in kwargs.items():
            options[key] = val
        self.options = options

    def update_options(self, **kwargs):
        for key, val in kwargs.items():
            self.options[key] = val

    def get_series(self):
        return self.series

    def set_series(self, series):
        self.series = series

    def get_placement(self):
        return None

    def set_placement(self, to):
        pass

    def set_constraints(self, constraints):
        self.constraints
