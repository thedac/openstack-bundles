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

import argparse
import logging
import os
import yaml

from common.charm import Charm
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


def override(args, charms, relations):
    # TODO
    # Like merge but use Charm.update or charm.set_options(update=True)
    pass


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--bundle', action='store_true')
    group.add_argument('-g', '--generate', action='store_true')
    parser.add_argument('-o', '--override')
    parser.add_argument('-d', '--destination', default="rendered.yaml")
    parser.add_argument('-s', '--series', default="xenial")
    parser.add_argument('-r', '--release', default="mitaka")
    parser.add_argument('-l', '--source', default="stable")
    return parser.parse_args()


def generate_bundle(args):
    charms = []

    # Get charm objects
    for charm in BASE_CHARMS:
        charm_obj = Charm(charm)
        charm_obj.set_series(args.series)
        charm_obj.set_url(args.source)
        charms.append(charm_obj)

    # Check for location overrides
    for charm in charms:
        if charm.name in LOCATION_OVERRIDES.keys():
            charm.set_url(LOCATION_OVERRIDES[charm.name],
                          custom_url=True)
    # Get relations
    relations = BASE_RELATIONS

    return charms, relations


def get_bundle_from_yaml(target=None):
    # TODO
    pass


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


def main():
    args = get_args()
    if args.generate:
        charms, relations = generate_bundle(args)
    else:
        charms, relations = get_bundle_from_yaml()

    if args.override:
        override(args, charms, relations)

    write_bundle(args, get_bundle_dict(charms, relations))


if __name__ == '__main__':
    main()
