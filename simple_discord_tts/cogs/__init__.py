from .read_queue_task import ReadQueueCog
from .clear_command import ClearCog
from .vc_command import ControlCommand

all_cogs = [
    ReadQueueCog,
    ClearCog,
    ControlCommand,
]
