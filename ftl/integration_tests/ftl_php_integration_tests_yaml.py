"""A script to generate a cloudbuild yaml."""

import os
import yaml

import util

# Add directories for new tests here.
TEST_DIRS = [
    'destination_test', 'metadata_test', 'lock_test',
    'empty_descriptor_test', 'no_descriptor_test',
    'no_deps_test', 'additional_directory',
    'gcp_build_test'
]

_ST_IMAGE = ('gcr.io/gcp-runtimes/structure-test:'
             '6195641f5a5a14c63c7945262066270842150ddb')
_TEST_DIR = '/workspace/ftl/php/testdata'
_PHP_BASE = 'gcr.io/gae-runtimes/php72_app_builder:argo_current'


def main():

    cloudbuild_yaml = util.INITIAL_CLOUDBUILD_YAML
    cloudbuild_yaml['steps'].append(
        # Build the FTL image from source and load it into the daemon.
        {
            'name': 'gcr.io/cloud-builders/bazel@sha256:7360c36bded15db68a35cfb1740a994f0a09ad5ce378a97f96d698bc223e442a',
            'args': ['run', '//ftl:php_builder_image', '--', '--norun'],
            'id': 'build-builder',
        }, )

    # Generate a set of steps for each test and add them.
    test_map = {}
    for test in TEST_DIRS:
        test_map[test] = [
            '--base', _PHP_BASE, '--name',
            'gcr.io/ftl-node-test/%s-image:latest' % test, '--directory',
            os.path.join(_TEST_DIR, test), '--no-cache'
        ]
    test_map['destination_test'].extend(['--destination', '/alternative-app'])
    test_map['metadata_test'].extend(['--entrypoint', '/bin/echo'])
    test_map['metadata_test'].extend(['--exposed-ports', '8090,8091'])
    test_map['additional_directory'].extend([
        '--additional-directory',
        '/workspace/ftl/php/testdata/additional_directory'
    ])

    for test, args in test_map.iteritems():
        cloudbuild_yaml['steps'] += util.run_test_steps(
            'php_builder_image', 'gcr.io/ftl-node-test/%s-image:latest' % test,
            os.path.join(_TEST_DIR, test), args)

    print yaml.dump(cloudbuild_yaml)


if __name__ == "__main__":
    main()
