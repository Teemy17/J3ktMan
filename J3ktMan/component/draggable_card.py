from reflex.components.radix.themes.components.card import Card

import reflex as rx


class DraggableCard(Card):
    """
    Wrapper over `rx.card` allowing handling of drag events.
    """

    on_drag_start: rx.EventHandler[lambda: []]
    on_drag_end: rx.EventHandler[lambda: []]


draggable_card = DraggableCard.create
