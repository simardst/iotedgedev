import json
import os

import pytest

from iotedgedev.deploymentmanifest import DeploymentManifest
from iotedgedev.envvars import EnvVars
from iotedgedev.output import Output
from iotedgedev.utility import Utility

from .utility import assert_list_equal

pytestmark = pytest.mark.unit

tests_dir = os.path.join(os.getcwd(), "tests")
test_assets_dir = os.path.join(tests_dir, "assets")
test_file_1 = os.path.join(test_assets_dir, "deployment.template_1.json")
test_file_2 = os.path.join(test_assets_dir, "deployment.template_2.json")
test_file_3 = os.path.join(test_assets_dir, "deployment.template_3.json")


@pytest.fixture
def deployment_manifest():
    output = Output()
    envvars = EnvVars(output)
    envvars.load()
    utility = Utility(envvars, output)

    def _deployment_manifest(path):
        return DeploymentManifest(envvars, output, utility, path, True)

    return _deployment_manifest


def test_get_desired_property(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    props = deployment_manifest.get_desired_property("$edgeHub", "schemaVersion")
    assert props == "1.0"


def test_get_desired_property_nonexistent_module(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    with pytest.raises(KeyError):
        deployment_manifest.get_desired_property("nonexistentModule", "schemaVersion")


def test_get_desired_property_nonexistent_prop(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    with pytest.raises(KeyError):
        deployment_manifest.get_desired_property("$edgeHub", "nonexistentProp")


def test_get_user_modules(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    user_modules = deployment_manifest.get_user_modules()
    assert_list_equal(user_modules, ["tempSensor", "csharpmodule", "csharpfunction"])


def test_get_system_modules(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    system_modules = deployment_manifest.get_system_modules()
    assert_list_equal(system_modules, ["edgeAgent", "edgeHub"])


def test_get_modules_to_process(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    modules_to_process = deployment_manifest.get_modules_to_process()
    assert_list_equal(modules_to_process, [("csharpmodule", "amd64"), ("csharpfunction", "amd64.debug")])


def test_get_modules_to_process_empty(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_2)
    modules_to_process = deployment_manifest.get_modules_to_process()
    assert_list_equal(modules_to_process, [])


def test_add_module_template(deployment_manifest):
    deployment_manifest = deployment_manifest(test_file_1)
    deployment_manifest.add_module_template("csharpmodule2")
    with open(test_file_3, "r") as expected:
        assert deployment_manifest.json == json.load(expected)
