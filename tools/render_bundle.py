#!/usr/bin/env python3
#
# Copyright 2017 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# TODO: Handle merge yaml files
# TODO: -HA switch which adds the required elements

import argparse
import logging
import os
import yaml

from common.charm import Charm
from common.tools_common import render_target_inheritance
import common.control_data_common as control_data
from common.base_constants import (
    BASE_CHARMS,
    BASE_RELATIONS,
    LOCATION_OVERRIDES,
)


def get_yaml_dict(filename):
    if os.path.isfile(filename):
        with open(filename) as yamlfile:
            try:
                return yaml.load(yamlfile)
            except yaml.parser.ParserError as e:
                logging.error("Invalid YAML:{}".format(e))
            except yaml.constructor.ConstructorError as e:
                logging.error("Invalid YAML: Likely templating "
                              "{{{{variable}}}} breaking YAML".format(e))
    else:
        logging.error("Not a file:", filename)


def merge_overrides(args, charms, relations):
    # TODO
    for yamlfile in args.overrides:
        # Like merge but use Charm.update(name, charm_dict=charm_dict)
        pass
    return charms, relations


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--bundle')
    group.add_argument('-g', '--generate', action='store_true')
    parser.add_argument('-o', '--overrides', nargs='*')
    parser.add_argument('-d', '--destination', default="rendered.yaml")
    parser.add_argument('-s', '--series', default="xenial")
    parser.add_argument('-r', '--release', default="mitaka")
    parser.add_argument('-src', '--source', default="stable")
    parser.add_argument('-t', '--target')
    parser.add_argument('-l', '--log_level', default="INFO")
    return parser.parse_args()


def generate_bundle(args):
    charms = []

    # Get charm objects
    for charm in BASE_CHARMS:
        charm_obj = Charm(charm)
        charm_obj.set_series(args.series)
        charm_obj.set_url(args.source)
        charms.append(charm_obj)

    # Get relations
    relations = BASE_RELATIONS

    return charms, relations


def set_urls(args, charms):
    # Set urls based on args.source
    logging.info("Setting charm urls based on source.")
    for charm in charms:
        charm.set_series(args.series)
        charm.set_url(args.source)

    # Check for location overrides
    for charm in charms:
        if charm.name in LOCATION_OVERRIDES.keys():
            charm.set_url(LOCATION_OVERRIDES[charm.name],
                          custom_url=True)


def set_origin(args, charms):
    if not args.target:
        logging.warn("Target not set. Not setting openstack-orgin and source")
    series, release = args.target.split('-')
    # Set origin based on target
    logging.info("Setting openstack-orgin and source based on target")
    for charm in charms:
        if ((series not in control_data.NATIVE_RELEASES.keys()) or
                release != control_data.NATIVE_RELEASES[series]):
            charm.set_origin(args.target)


def get_bundle_from_yaml(args):
    charms = []
    relations = []
    bundle_dict = get_yaml_dict(args.bundle)

    # The render_target_inheritance function has this note:
    #   - Use an override keys map to determine which charms and config
    #     overrides are valid for the charm.
    #
    #   - juju-deployer branches and inspects config.yaml of each charm
    #     to determine valid config override keys, whereas this to
    #     does not do charm code retrieval.
    #
    # It may be a good idea to mimic juju-deployer to allow more flexible
    # overrides. Otherwise, we are stuck managing a static constants that can
    # become out of date.
    if args.target:
        bundle_dict = render_target_inheritance(bundle_dict, args.target)

    # Get charm objects
    for charm in bundle_dict['services']:
        charm_obj = Charm(charm, charm_dict={charm:
                                             bundle_dict['services'][charm]})
        charms.append(charm_obj)

    for relation in bundle_dict['relations']:
        relations.append(relation)

    return charms, relations


def get_bundle_dict(charms, relations,
                    machines=None, networks=None):
    bundle_dict = {'services': {}, 'relations': {}}

    for charm in charms:
        bundle_dict['services'][charm.name] = charm.get_dict()[charm.name]

    bundle_dict['relations'] = relations

    return bundle_dict


def write_bundle(args, bundle_data):
    with open(args.destination, 'w') as dest:
        dest.write(yaml.dump(bundle_data))


def set_log_level(args):
    logging.basicConfig(level=args.log_level.upper())


def main():
    args = get_args()
    set_log_level(args)

    if args.generate:
        charms, relations = generate_bundle(args)
    else:
        charms, relations = get_bundle_from_yaml(args)

    # Merge
    if args.overrides:
        charms, relations = merge_overrides(args, charms, relations)

    # Set urls based on args.source
    set_urls(args, charms)
    # Set openstack-origin and source
    set_origin(args, charms)

    write_bundle(args, get_bundle_dict(charms, relations))


if __name__ == '__main__':
    main()
