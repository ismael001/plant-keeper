"""
Celery + Redis async tasks
"""

from line_protocol_parser import parse_line
from django.core.exceptions import ObjectDoesNotExist
from core.controller import TimeRangeController
from light.models import Light
from light.dict_def import LightCtrlDict
from project.settings import MQTT_HOST
from project.settings import MQTT_PORT
from project.settings import MQTT_USER
from project.settings import MQTT_PASSWORD
from project.settings import MQTT_LIGHT_CONTROLLER_TOPIC
from celery.decorators import task
import paho.mqtt.client as mqtt
import orjson as json
from datetime import time

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username=MQTT_USER, password=MQTT_PASSWORD)
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)


@task(name="light_control")
def node_controller(message):
    """
    async task : read message from mqtt,
    apply controller rules
    write on message on MQTT topic
    :param message:
    :return:
    """
    d: dict = parse_line(message + b' 0')
    tag: str = d['tags']['tag']
    light = Light()
    ctl = TimeRangeController()
    try:
        light.get_config(tag)
    except ObjectDoesNotExist:
        light.update_config(
            tag=tag,
            on_time_at=time(hour=9, minute=0, second=0),
            off_time_at=time(hour=18, minute=0, second=0)
        )
        light.get_config(tag)
    ctl.set_conf(
        start_at=light.on_time_at,
        end_at=light.off_time_at,
    )
    signal = ctl.get_signal()

    light.update_controller(
        tag=tag,
        light_signal=bool(signal)
    )

    mqtt_client.publish(
        MQTT_LIGHT_CONTROLLER_TOPIC,
        json.dumps(
            LightCtrlDict(
                controller_type="light",
                tag=tag,
                on_time_at="",
                off_time_at="",
                light_signal=bool(signal)
            )
        )
    )