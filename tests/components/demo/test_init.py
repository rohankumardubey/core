"""The tests for the Demo component."""
from contextlib import suppress
import json
import os

import pytest

from homeassistant.components.demo import DOMAIN
from homeassistant.components.device_tracker.legacy import YAML_DEVICES
from homeassistant.components.recorder.statistics import list_statistic_ids
from homeassistant.helpers.json import JSONEncoder
from homeassistant.setup import async_setup_component, setup_component

from tests.components.recorder.common import wait_recording_done


@pytest.fixture(autouse=True)
def mock_history(hass):
    """Mock history component loaded."""
    hass.config.components.add("history")


@pytest.fixture(autouse=True)
def demo_cleanup(hass):
    """Clean up device tracker demo file."""
    yield
    with suppress(FileNotFoundError):
        os.remove(hass.config.path(YAML_DEVICES))


async def test_setting_up_demo(hass):
    """Test if we can set up the demo and dump it to JSON."""
    assert await async_setup_component(hass, DOMAIN, {DOMAIN: {}})
    await hass.async_block_till_done()
    await hass.async_start()

    # This is done to make sure entity components don't accidentally store
    # non-JSON-serializable data in the state machine.
    try:
        json.dumps(hass.states.async_all(), cls=JSONEncoder)
    except Exception:  # pylint: disable=broad-except
        pytest.fail(
            "Unable to convert all demo entities to JSON. "
            "Wrong data in state machine!"
        )


def test_demo_statistics(hass_recorder):
    """Test that the demo components makes some statistics available."""
    hass = hass_recorder()

    assert setup_component(hass, DOMAIN, {DOMAIN: {}})
    hass.block_till_done()
    hass.start()
    wait_recording_done(hass)

    statistic_ids = list_statistic_ids(hass)
    assert {
        "name": None,
        "source": "demo",
        "statistic_id": "demo:temperature_outdoor",
        "unit_of_measurement": "°C",
    } in statistic_ids
    assert {
        "name": None,
        "source": "demo",
        "statistic_id": "demo:energy_consumption",
        "unit_of_measurement": "kWh",
    } in statistic_ids
