"""Qt bridge: presentation signals in, domain events out."""

from __future__ import annotations

from .domain import InstallCommand, InstallEvent, InstallWorkflow


class InstallController:
    def __init__(self) -> None:
        self.workflow = InstallWorkflow()
        self.listeners = []

    def subscribe(self, listener) -> None:
        self.listeners.append(listener)

    def dispatch(self, command: InstallCommand, **details) -> InstallEvent:
        event = self.workflow.dispatch(command, **details)
        for listener in tuple(self.listeners):
            listener(event)
        return event
