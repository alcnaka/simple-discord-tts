from .read_queue_task import ReadQueueCog
from .clear_command import ClearCog
from .vc_command import ControlCommand
from .voice_state_listener import VoiceStateListenerCog

all_cogs = [
    ReadQueueCog,
    ClearCog,
    ControlCommand,
    VoiceStateListenerCog,
]
