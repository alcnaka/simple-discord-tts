from .admin_commands import AdminCommands
from .clear_command import ClearCog
from .read_queue_task import ReadQueueCog
from .vc_command import ControlCommand
from .voice_state_listener import VoiceStateListenerCog

all_cogs = [
    AdminCommands,
    ClearCog,
    ReadQueueCog,
    ControlCommand,
    VoiceStateListenerCog,
]
