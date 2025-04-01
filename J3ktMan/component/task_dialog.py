from J3ktMan.crud.tasks import (
    ExistingTaskNameError,
    assign_milestone,
    delete_task,
    rename_task,
    set_task_description,
)
from reflex.event import EventSpec
import reflex as rx


class State(rx.State):
    _editing_task_id: int | None = None
    _editing_task_name: str | None = None
    _editing_task_description: str | None = None

    _last_task_renamed: str | None = None
    _last_task_description_set: str | None = None
    _last_assigned_milestone_id: int | None = None

    @rx.var
    def editing_task_id(self) -> int | None:
        return self._editing_task_id

    @rx.var
    def last_task_renamed(self) -> str | None:
        return self._last_task_renamed

    @rx.var
    def last_task_description_set(self) -> str | None:
        return self._last_task_description_set

    @rx.var
    def last_assigned_milestone_id(self) -> int | None:
        return self._last_assigned_milestone_id

    @rx.event
    def set_editing_task_id(self, task_id: int, open: bool):
        if open:
            self.reset()
            self._editing_task_id = task_id
        else:
            self._editing_task_id = None

    @rx.event
    def reset_state(self):
        self._editing_task_id = None
        self._editing_task_name = None
        self._editing_task_description = None

    @rx.var(cache=True)
    def is_editing_task_name(self) -> bool:
        return self._editing_task_name is not None

    @rx.var(cache=True)
    def is_editing_task_description(self) -> bool:
        return self._editing_task_description is not None

    @rx.event
    def update_task_editing_name(self, value: str):
        self._editing_task_name = value

    @rx.event
    def update_task_editing_description(self, value: str | None):
        self._editing_task_description = value

    @rx.event
    async def confirm_editing_task_name(self) -> list[EventSpec] | None:
        if self._editing_task_id is None or self._editing_task_name is None:
            return

        new_task_name = self._editing_task_name
        self._editing_task_name = None

        try:
            new_task_model = rename_task(self._editing_task_id, new_task_name)
            self._last_task_renamed = new_task_model.name

            return [
                rx.toast.success(
                    f'Task renamed to "{new_task_name}" successfully',
                    position="top-center",
                )
            ]

        except ExistingTaskNameError:
            self._last_task_renamed = None

            return [
                rx.toast.error(
                    f'Task with name"{new_task_name}" already exists',
                    position="top-center",
                )
            ]

    @rx.event
    async def confirm_editing_task_description(self) -> list[EventSpec] | None:
        if (
            self._editing_task_id is None
            or self._editing_task_description is None
        ):
            return

        new_task_description = self._editing_task_description
        self._editing_task_description = None

        new_task_model = set_task_description(
            self._editing_task_id, new_task_description
        )
        self._last_task_description_set = new_task_model.description

        return [
            rx.toast.success(
                "New description saved",
                position="top-center",
            )
        ]

    @rx.event
    async def delete_task(self, task_name: str) -> list[EventSpec] | None:
        if self._editing_task_id is None:
            return

        delete_task(self._editing_task_id)

        return [
            rx.toast.success(
                f'Task "{task_name}" deleted', position="top-center"
            )
        ]

    @rx.event
    async def assign_milestone(
        self,
        task_name: str,
        milestone_id: str | None,
        milestone_names_by_id: dict[str, str],
    ) -> list[EventSpec] | None:
        # `milestone_names_by_id` and `milestone_id` because it's passed as
        # a json where the key is always strings LMAOO
        if self._editing_task_id is None:
            return

        assign_milestone(
            int(milestone_id) if milestone_id else None, self._editing_task_id
        )

        self._last_assigned_milestone_id = (
            int(milestone_id) if milestone_id else None
        )

        message = (
            f'Task "{task_name}" has been assigned to "{milestone_names_by_id[milestone_id]}"'  # type: ignore
            if milestone_id is not None
            else f'Task "{task_name}" has been unassigned'
        )

        return [
            rx.toast.success(message, position="top-center"),
        ]


def _make_handler(base, additional):
    on_submit = [base]

    if additional is not None:
        if isinstance(additional, list):
            for x in additional:
                on_submit.append(x)
        else:
            on_submit.append(additional)

    return on_submit


def task_dialog_content(
    task_name: str,
    task_description: rx.Var[str] | str,
    current_milestone_id: int | None,
    milestone_names_by_id: rx.Var[dict[int, str]] | dict[int, str],
    on_task_name_edit=None,
    on_task_description_edit=None,
    on_assign_milestone=None,
    on_task_delete=None,
) -> rx.Component:
    return rx.dialog.content(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="list-todo"),
                    radius="full",
                    padding="0.65rem",
                ),
                rx.cond(  # type: ignore
                    State.is_editing_task_name,
                    rx.form(
                        rx.input(
                            value=rx.cond(
                                State._editing_task_name,
                                State._editing_task_name,
                                "",
                            ),
                            variant="soft",
                            background_color="transparent",
                            placeholder="Task Name",
                            auto_focus=True,
                            size="3",
                            content_editable=True,
                            width="100%",
                            on_change=State.update_task_editing_name,
                            on_blur=_make_handler(  # type: ignore
                                State.confirm_editing_task_name,
                                on_task_name_edit,
                            ),
                        ),
                        reset_on_submit=False,
                        on_submit=_make_handler(  # type:ignore
                            State.confirm_editing_task_name,
                            on_task_name_edit,
                        ),
                    ),
                    rx.heading(
                        task_name,
                        size="4",
                        width="100%",
                        on_click=State.update_task_editing_name(task_name),
                    ),
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.fragment(
                                rx.cond(
                                    current_milestone_id,
                                    milestone_names_by_id[  # type: ignore
                                        current_milestone_id
                                    ],
                                    "No Milestone",
                                ),
                                rx.icon("chevron-down", size=12),
                            ),
                            variant="soft",
                            color_scheme=rx.cond(
                                current_milestone_id,
                                "indigo",
                                "gray",
                            ),
                            auto_focus=False,
                        ),
                    ),
                    rx.menu.content(
                        rx.foreach(
                            milestone_names_by_id,
                            lambda test: rx.menu.item(
                                rx.icon("list-check", size=12),
                                test[1],
                                cursor="pointer",
                                on_click=_make_handler(
                                    State.assign_milestone(
                                        task_name,
                                        test[0],
                                        milestone_names_by_id,  # type:ignore
                                    ),
                                    on_assign_milestone,  # type: ignore
                                ),
                            ),
                        ),
                        rx.menu.separator(),
                        rx.menu.item(
                            "None",
                            color_scheme="gray",
                            on_click=_make_handler(
                                State.assign_milestone(
                                    task_name, None, milestone_names_by_id  # type: ignore
                                ),
                                on_assign_milestone,
                            ),
                        ),
                    ),
                ),
                rx.dialog.root(
                    rx.dialog.trigger(
                        rx.icon_button(
                            "trash-2", color_scheme="gray", variant="ghost"
                        )
                    ),
                    rx.dialog.content(
                        rx.vstack(
                            rx.hstack(
                                rx.badge(
                                    rx.icon(tag="trash-2"),
                                    color_scheme="red",
                                    radius="full",
                                    padding="0.65rem",
                                ),
                                rx.vstack(
                                    rx.heading(
                                        f'Delete Task "{task_name}"',
                                        size="4",
                                    ),
                                    rx.text(
                                        "Are you sure you want to delete this task?",
                                        size="2",
                                    ),
                                    spacing="1",
                                    align_items="start",
                                ),
                                align_items="center",
                                padding_bottom="1rem",
                            ),
                            rx.dialog.close(
                                rx.hstack(
                                    rx.button(
                                        "Cancel",
                                        variant="soft",
                                        color_scheme="gray",
                                        auto_focus=False,
                                    ),
                                    rx.button(
                                        "Delete",
                                        variant="soft",
                                        color_scheme="red",
                                        auto_focus=False,
                                        on_click=_make_handler(  # type: ignore
                                            State.delete_task(task_name),
                                            on_task_delete,
                                        ),
                                    ),
                                    class_name="self-end items-center mt-1",
                                )
                            ),
                        )
                    ),
                ),
                align_items="center",
                width="100%",
            ),
            rx.heading("Description", size="3", margin_y="0.25rem"),
            rx.cond(
                State.is_editing_task_description,
                rx.box(
                    rx.text_area(
                        value=State._editing_task_description,
                        width="100%",
                        on_change=State.update_task_editing_description,
                        auto_focus=True,
                        color_scheme="gray",
                        size="2",
                    ),
                    rx.hstack(
                        rx.button(
                            "Save",
                            on_click=_make_handler(  # type: ignore
                                State.confirm_editing_task_description,
                                on_task_description_edit,
                            ),
                            variant="soft",
                            margin_top="1rem",
                        ),
                        rx.button(
                            "Cancel",
                            on_click=State.update_task_editing_description(
                                None
                            ),
                            variant="soft",
                            margin_top="1rem",
                            color_scheme="gray",
                        ),
                    ),
                    width="100%",
                ),
                rx.box(
                    rx.cond(
                        task_description.length() > 0,  # type: ignore
                        rx.text(
                            task_description,
                            width="100%",
                            cursor="text",
                            class_name="hover:underline hover:italic",
                        ),
                        rx.text(
                            "No Description, Click to Edit",
                            font_style="italic",
                            color_scheme="gray",
                            width="100%",
                            cursor="text",
                            class_name="hover:underline",
                        ),
                    ),
                    on_click=State.update_task_editing_description(
                        task_description
                    ),
                ),
            ),
        ),
        width="80rem",
    )


def task_dialog(
    trigger: rx.Component,
    task_name: str,
    task_description: rx.Var[str] | str,
    current_milestone_id: int | None,
    milestone_names_by_id: rx.Var[dict[int, str]] | dict[int, str],
    task_id: int,
    on_task_name_edit=None,
    on_task_description_edit=None,
    on_assign_milestone=None,
    on_delete_task=None,
) -> rx.Component:
    return rx.dialog(
        trigger,
        task_dialog_content(
            task_name,
            task_description,
            current_milestone_id,
            milestone_names_by_id,
            on_task_name_edit=on_task_name_edit,
            on_task_description_edit=on_task_description_edit,
            on_assign_milestone=on_assign_milestone,
            on_task_delete=on_delete_task,
        ),
        open=State.editing_task_id == task_id,
        on_open_change=lambda e: State.set_editing_task_id(task_id, e),
    )
