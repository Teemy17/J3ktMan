from reflex.components.radix.themes.layout.box import Box

import reflex as rx


class DragZone(Box):
    """
    A wrapper over `rx.box` allowing handling of drag events.
    """

    on_drag_enter: rx.EventHandler[lambda e: [e]]
    on_drop: rx.EventHandler[lambda e: [e]]
    on_drag_leave: rx.EventHandler[lambda e: [e]]
    on_drag_over: rx.EventHandler[lambda e: [e]]
    


drag_zone = DragZone.create
