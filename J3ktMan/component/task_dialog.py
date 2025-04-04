# from J3ktMan.state.project import State as ProjectState, Data
# from J3ktMan.utils import date_to_epoch, epoch_to_date
# from reflex.event import EventSpec
# import reflex as rx


# class State(rx.State):
#     _editing_task_id: int | None = None
#     _editing_task_name: str | None = None
#     _editing_task_description: str | None = None

#     @rx.var
#     def editing_task_id(self) -> int | None:
#         return self._editing_task_id

#     @rx.event
#     def set_editing_task_id(self, task_id: int, open: bool):
#         if open:
#             self.reset()
#             self._editing_task_id = task_id
#         else:
#             self._editing_task_id = None

#     @rx.event
#     def reset_state(self):
#         self._editing_task_id = None
#         self._editing_task_name = None
#         self._editing_task_description = None
#         self._editing_task_start_date = None
#         self._editing_task_end_date = None

#     @rx.var(cache=True)
#     def is_editing_task_name(self) -> bool:
#         return self._editing_task_name is not None

#     @rx.var(cache=True)
#     def is_editing_task_description(self) -> bool:
#         return self._editing_task_description is not None

#     @rx.event
#     def update_task_editing_name(self, value: str):
#         self._editing_task_name = value

#     @rx.event
#     def update_task_editing_description(self, value: str | None):
#         self._editing_task_description = value

#     @rx.event
#     def update_task_editing_start_date(self, value: str | None):
#         self._editing_task_start_date = date_to_epoch(value)  # type: ignore

#     @rx.event
#     def update_task_editing_end_date(self, value: str | None):
#         self._editing_task_end_date = date_to_epoch(value)  # type: ignore

#     @rx.event
#     async def confirm_editing_task_name(self) -> list[EventSpec] | None:
#         if self._editing_task_id is None or self._editing_task_name is None:
#             return

#         new_task_name = self._editing_task_name
#         self._editing_task_name = None

#         state = await self.get_state(ProjectState)
#         return state.rename_task(self._editing_task_id, new_task_name)

#     @rx.event
#     async def confirm_editing_task_description(self) -> list[EventSpec] | None:
#         if (
#             self._editing_task_id is None
#             or self._editing_task_description is None
#         ):
#             return

#         new_task_description = self._editing_task_description
#         self._editing_task_description = None

#         state = await self.get_state(ProjectState)
#         return state.set_task_description(
#             self._editing_task_id, new_task_description
#         )

#     @rx.event
#     async def edit_task_date(self) -> list[EventSpec] | None:
#         if self._editing_task_id is None:
#             return

#         state = await self.get_state(ProjectState)
#         return state.change_task_dates(
#             self._editing_task_id, start_date=None, end_date=None
#         )

#     @rx.event
#     async def delete_task(self) -> list[EventSpec] | None:
#         if self._editing_task_id is None:
#             return

#         task_id = self._editing_task_id
#         self._editing_task_id = None

#         state = await self.get_state(ProjectState)
#         return state.delete_task(task_id)


# def _make_handler(base, additional):
#     on_submit = [base]

#     if additional is not None:
#         if isinstance(additional, list):
#             for x in additional:
#                 on_submit.append(x)
#         else:
#             on_submit.append(additional)

#     return on_submit


# def task_dialog_content(
#     task_id: int,
#     on_task_name_edit=None,
#     on_task_description_edit=None,
#     on_assign_milestone=None,
#     on_task_delete=None,
#     on_task_date_edit=None,
# ) -> rx.Component:
#     data: Data = ProjectState.data  # type: ignore

#     return rx.dialog.content(
#         rx.vstack(
#             rx.hstack(
#                 rx.badge(
#                     rx.icon(tag="list-todo"),
#                     radius="full",
#                     padding="0.65rem",
#                 ),
#                 rx.cond(  # type: ignore
#                     State.is_editing_task_name,
#                     rx.form(
#                         rx.input(
#                             value=rx.cond(
#                                 State._editing_task_name,
#                                 State._editing_task_name,
#                                 "",
#                             ),
#                             variant="soft",
#                             background_color="transparent",
#                             placeholder="Task Name",
#                             auto_focus=True,
#                             size="3",
#                             content_editable=True,
#                             width="100%",
#                             on_change=State.update_task_editing_name,
#                             on_blur=_make_handler(  # type: ignore
#                                 State.confirm_editing_task_name,
#                                 on_task_name_edit,
#                             ),
#                         ),
#                         reset_on_submit=False,
#                         on_submit=_make_handler(  # type:ignore
#                             State.confirm_editing_task_name,
#                             on_task_name_edit,
#                         ),
#                     ),
#                     rx.heading(
#                         data.tasks_by_id[task_id].name,
#                         size="4",
#                         width="100%",
#                         on_click=State.update_task_editing_name(
#                             data.tasks_by_id[task_id].name
#                         ),
#                     ),
#                 ),
#                 rx.menu.root(
#                     rx.menu.trigger(
#                         rx.button(
#                             rx.fragment(
#                                 rx.cond(
#                                     data.tasks_by_id[task_id].milestone_id,
#                                     data.milestones_by_id[  # type: ignore
#                                         data.tasks_by_id[task_id].milestone_id
#                                     ].name,
#                                     "No Milestone",
#                                 ),
#                                 rx.icon(tag="chevron-down", size=12),
#                             ),
#                             variant="soft",
#                             color_scheme=rx.cond(
#                                 data.tasks_by_id[task_id].milestone_id,
#                                 "indigo",
#                                 "gray",
#                             ),
#                             auto_focus=False,
#                         ),
#                     ),
#                     rx.menu.content(
#                         rx.foreach(
#                             ProjectState.milestones,
#                             lambda milestone: rx.menu.item(
#                                 rx.icon(tag="list-check", size=12),
#                                 milestone.name,
#                                 cursor="pointer",
#                                 on_click=_make_handler(  # type: ignore
#                                     ProjectState.assign_milestone(
#                                         task_id,
#                                         milestone.id,
#                                     ),
#                                     on_assign_milestone,
#                                 ),
#                             ),
#                         ),
#                         rx.menu.separator(),
#                         rx.menu.item(
#                             "None",
#                             color_scheme="gray",
#                             on_click=_make_handler(  # type: ignore
#                                 ProjectState.assign_milestone(
#                                     task_id,
#                                     None,
#                                 ),
#                                 on_assign_milestone,
#                             ),
#                         ),
#                     ),
#                 ),
#                 rx.dialog.root(
#                     rx.dialog.trigger(
#                         rx.button(
#                             rx.icon(tag="calendar"),
#                             color_scheme="pink",
#                             variant="ghost",
#                         )
#                     ),
#                     rx.dialog.content(
#                         rx.vstack(
#                             rx.hstack(
#                                 rx.badge(
#                                     rx.icon(tag="calendar"),
#                                 ),
#                                 rx.vstack(
#                                     rx.dialog.title(
#                                         "Edit Task Dates",
#                                     ),
#                                     rx.dialog.description(
#                                         "Edit the start and end dates of the task.",
#                                     ),
#                                     spacing="1",
#                                     align_items="start",
#                                 ),
#                                 padding_bottom="1rem",
#                             ),
#                             rx.hstack(
#                                 rx.form.root(
#                                     rx.text(
#                                         "Start Date",
#                                         size="2",
#                                         margin_bottom="4px",
#                                         weight="bold",
#                                     ),
#                                     rx.input(
#                                         type="date",
#                                         value=epoch_to_date(  # type: ignore
#                                             data.tasks_by_id[task_id].start_date  # type: ignore
#                                         ),
#                                         on_change=State.update_task_editing_start_date,
#                                         width="100%",
#                                     ),
#                                     rx.text(
#                                         "End Date",
#                                         size="2",
#                                         margin_bottom="4px",
#                                         weight="bold",
#                                     ),
#                                     rx.input(
#                                         type="date",
#                                         value=epoch_to_date(  # type: ignore
#                                             data.tasks_by_id[task_id].end_date  # type: ignore
#                                         ),
#                                         on_change=State.update_task_editing_end_date,
#                                         width="100%",
#                                     ),
#                                     rx.button(
#                                         "Save",
#                                         on_click=_make_handler(  # type: ignore
#                                             State.edit_task_date,
#                                             on_task_date_edit,
#                                         ),
#                                         variant="soft",
#                                         margin_top="1rem",
#                                     ),
#                                     on_submit=_make_handler(  # type: ignore
#                                         State.edit_task_date,
#                                         on_task_date_edit,
#                                     ),
#                                 ),
#                                 rx.button(
#                                     "Cancel",
#                                     on_click=State.edit_task_date(),
#                                     variant="soft",
#                                     margin_top="1rem",
#                                     color_scheme="gray",
#                                 ),
#                                 class_name="self-end items-center mt-1",
#                             ),
#                         )
#                     ),
#                 ),
#                 rx.dialog.root(
#                     rx.dialog.trigger(
#                         rx.button(
#                             rx.icon(tag="trash-2"),
#                             color_scheme="gray",
#                             variant="ghost",
#                         )
#                     ),
#                     rx.dialog.content(
#                         rx.vstack(
#                             rx.hstack(
#                                 rx.badge(
#                                     rx.icon(tag="trash-2"),
#                                     color_scheme="red",
#                                     radius="full",
#                                     padding="0.65rem",
#                                 ),
#                                 rx.vstack(
#                                     rx.heading(
#                                         f'Delete Task "{data.tasks_by_id[task_id].name}"',
#                                         size="4",
#                                     ),
#                                     rx.text(
#                                         "Are you sure you want to delete this task?",
#                                         size="2",
#                                     ),
#                                     spacing="1",
#                                     align_items="start",
#                                 ),
#                                 align_items="center",
#                                 padding_bottom="1rem",
#                             ),
#                             rx.dialog.close(
#                                 rx.hstack(
#                                     rx.button(
#                                         "Cancel",
#                                         variant="soft",
#                                         color_scheme="gray",
#                                         auto_focus=False,
#                                     ),
#                                     rx.button(
#                                         "Delete",
#                                         variant="soft",
#                                         color_scheme="red",
#                                         auto_focus=False,
#                                         on_click=_make_handler(  # type: ignore
#                                             State.delete_task,
#                                             on_task_delete,
#                                         ),
#                                     ),
#                                     class_name="self-end items-center mt-1",
#                                 )
#                             ),
#                         )
#                     ),
#                 ),
#                 align_items="center",
#                 width="100%",
#             ),
#             rx.heading("Description", size="3", margin_y="0.25rem"),
#             rx.cond(
#                 State.is_editing_task_description,
#                 rx.box(
#                     rx.text_area(
#                         value=State._editing_task_description,
#                         width="100%",
#                         on_change=State.update_task_editing_description,
#                         auto_focus=True,
#                         color_scheme="gray",
#                         size="2",
#                     ),
#                     rx.hstack(
#                         rx.button(
#                             "Save",
#                             on_click=_make_handler(  # type: ignore
#                                 State.confirm_editing_task_description,
#                                 on_task_description_edit,
#                             ),
#                             variant="soft",
#                             margin_top="1rem",
#                         ),
#                         rx.button(
#                             "Cancel",
#                             on_click=State.update_task_editing_description(
#                                 None
#                             ),
#                             variant="soft",
#                             margin_top="1rem",
#                             color_scheme="gray",
#                         ),
#                     ),
#                     width="100%",
#                 ),
#                 rx.box(
#                     rx.cond(
#                         data.tasks_by_id[task_id].description.length() > 0,  # type: ignore
#                         rx.text(
#                             data.tasks_by_id[task_id].description,
#                             width="100%",
#                             cursor="text",
#                             class_name="hover:underline hover:italic",
#                         ),
#                         rx.text(
#                             "No Description, Click to Edit",
#                             font_style="italic",
#                             color_scheme="gray",
#                             width="100%",
#                             cursor="text",
#                             class_name="hover:underline",
#                         ),
#                     ),
#                     on_click=State.update_task_editing_description(
#                         data.tasks_by_id[task_id].description
#                     ),
#                 ),
#             ),
#         ),
#         width="80rem",
#     )

from J3ktMan.state.project import State as ProjectState, Data
from J3ktMan.utils import date_to_epoch, epoch_to_date
from reflex.event import EventSpec
import reflex as rx


class State(rx.State):
    _editing_task_id: int | None = None
    _editing_task_name: str | None = None
    _editing_task_description: str | None = None
    _editing_task_start_date: int | None = None
    _editing_task_end_date: int | None = None

    @rx.var
    def editing_task_id(self) -> int | None:
        return self._editing_task_id

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
        self._editing_task_start_date = None
        self._editing_task_end_date = None

    @rx.var(cache=True)
    def is_editing_task_name(self) -> bool:
        return self._editing_task_name is not None

    @rx.var(cache=True)
    def is_editing_task_description(self) -> bool:
        return self._editing_task_description is not None

    @rx.var
    def editing_task_start_date(self) -> str | None:
        if self._editing_task_start_date is not None:
            return epoch_to_date(self._editing_task_start_date)
        return None

    @rx.var
    def editing_task_end_date(self) -> str | None:
        if self._editing_task_end_date is not None:
            return epoch_to_date(self._editing_task_end_date)
        return None

    @rx.var(cache=True)
    def is_editing_task_dates(self) -> bool:
        return (
            self._editing_task_start_date is not None
            or self._editing_task_end_date is not None
        )

    @rx.event
    def update_task_editing_name(self, value: str):
        self._editing_task_name = value

    @rx.event
    def update_task_editing_description(self, value: str | None):
        self._editing_task_description = value

    @rx.event
    def update_task_editing_start_date(self, value: str | None):
        self._editing_task_start_date = date_to_epoch(value) if value else None

    @rx.event
    def update_task_editing_end_date(self, value: str | None):
        self._editing_task_end_date = date_to_epoch(value) if value else None

    @rx.event
    async def confirm_editing_task_name(self) -> list[EventSpec] | None:
        if self._editing_task_id is None or self._editing_task_name is None:
            return

        new_task_name = self._editing_task_name
        self._editing_task_name = None

        state = await self.get_state(ProjectState)
        return state.rename_task(self._editing_task_id, new_task_name)

    @rx.event
    async def confirm_editing_task_description(self) -> list[EventSpec] | None:
        if (
            self._editing_task_id is None
            or self._editing_task_description is None
        ):
            return

        new_task_description = self._editing_task_description
        self._editing_task_description = None

        state = await self.get_state(ProjectState)
        return state.set_task_description(
            self._editing_task_id, new_task_description
        )

    @rx.event
    async def confirm_editing_task_dates(self) -> list[EventSpec] | None:
        if self._editing_task_id is None:
            return

        start_date = self._editing_task_start_date
        end_date = self._editing_task_end_date
        self._editing_task_start_date = None
        self._editing_task_end_date = None

        state = await self.get_state(ProjectState)
        return state.change_task_dates(
            self._editing_task_id, start_date=start_date, end_date=end_date
        )

    @rx.event
    async def delete_task(self) -> list[EventSpec] | None:
        if self._editing_task_id is None:
            return

        task_id = self._editing_task_id
        self._editing_task_id = None

        state = await self.get_state(ProjectState)
        return state.delete_task(task_id)


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
    task_id: int,
    on_task_name_edit=None,
    on_task_description_edit=None,
    on_assign_milestone=None,
    on_task_delete=None,
    on_task_date_edit=None,
) -> rx.Component:
    data: Data = ProjectState.data

    return rx.dialog.content(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="list-todo"),
                    radius="full",
                    padding="0.65rem",
                ),
                rx.cond(
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
                            on_blur=_make_handler(
                                State.confirm_editing_task_name,
                                on_task_name_edit,
                            ),
                        ),
                        reset_on_submit=False,
                        on_submit=_make_handler(
                            State.confirm_editing_task_name,
                            on_task_name_edit,
                        ),
                    ),
                    rx.heading(
                        data.tasks_by_id[task_id].name,
                        size="4",
                        width="100%",
                        on_click=State.update_task_editing_name(
                            data.tasks_by_id[task_id].name
                        ),
                    ),
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.fragment(
                                rx.cond(
                                    data.tasks_by_id[task_id].milestone_id,
                                    data.milestones_by_id[
                                        data.tasks_by_id[task_id].milestone_id
                                    ].name,
                                    "No Milestone",
                                ),
                                rx.icon(tag="chevron-down", size=12),
                            ),
                            variant="soft",
                            color_scheme=rx.cond(
                                data.tasks_by_id[task_id].milestone_id,
                                "indigo",
                                "gray",
                            ),
                            auto_focus=False,
                        ),
                    ),
                    rx.menu.content(
                        rx.foreach(
                            ProjectState.milestones,
                            lambda milestone: rx.menu.item(
                                rx.icon(tag="list-check", size=12),
                                milestone.name,
                                cursor="pointer",
                                on_click=_make_handler(
                                    ProjectState.assign_milestone(
                                        task_id,
                                        milestone.id,
                                    ),
                                    on_assign_milestone,
                                ),
                            ),
                        ),
                        rx.menu.separator(),
                        rx.menu.item(
                            "None",
                            color_scheme="gray",
                            on_click=_make_handler(
                                ProjectState.assign_milestone(
                                    task_id,
                                    None,
                                ),
                                on_assign_milestone,
                            ),
                        ),
                    ),
                ),
                rx.dialog.root(
                    rx.dialog.trigger(
                        rx.button(
                            rx.icon(tag="calendar"),
                            color_scheme="pink",
                            variant="ghost",
                        )
                    ),
                    rx.dialog.content(
                        rx.vstack(
                            rx.hstack(
                                rx.badge(
                                    rx.icon(tag="calendar"),
                                ),
                                rx.vstack(
                                    rx.dialog.title(
                                        "Edit Task Dates",
                                    ),
                                    rx.dialog.description(
                                        "Edit the start and end dates of the task.",
                                    ),
                                    spacing="1",
                                    align_items="start",
                                ),
                                padding_bottom="1rem",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Start Date",
                                    size="2",
                                    margin_bottom="4px",
                                    weight="bold",
                                ),
                                rx.input(
                                    type="date",
                                    value=State.editing_task_start_date,
                                    on_change=State.update_task_editing_start_date,
                                    width="100%",
                                ),
                                rx.text(
                                    "End Date",
                                    size="2",
                                    margin_bottom="4px",
                                    weight="bold",
                                ),
                                rx.input(
                                    type="date",
                                    value=State.editing_task_end_date,
                                    on_change=State.update_task_editing_end_date,
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.button(
                                        "Save",
                                        on_click=_make_handler(
                                            State.confirm_editing_task_dates,
                                            on_task_date_edit,
                                        ),
                                        variant="soft",
                                        margin_top="1rem",
                                    ),
                                    rx.button(
                                        "Cancel",
                                        on_click=State.reset_state,
                                        variant="soft",
                                        margin_top="1rem",
                                        color_scheme="gray",
                                    ),
                                    class_name="self-end items-center mt-1",
                                ),
                            ),
                        )
                    ),
                ),
                rx.dialog.root(
                    rx.dialog.trigger(
                        rx.button(
                            rx.icon(tag="trash-2"),
                            color_scheme="gray",
                            variant="ghost",
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
                                        f'Delete Task "{data.tasks_by_id[task_id].name}"',
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
                                        on_click=_make_handler(
                                            State.delete_task,
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
                            on_click=_make_handler(
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
                        data.tasks_by_id[task_id].description.length() > 0,
                        rx.text(
                            data.tasks_by_id[task_id].description,
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
                        data.tasks_by_id[task_id].description
                    ),
                ),
            ),
        ),
        width="80rem",
    )


def task_dialog(
    trigger: rx.Component,
    task_id: int,
    on_task_name_edit=None,
    on_task_description_edit=None,
    on_assign_milestone=None,
    on_delete_task=None,
) -> rx.Component:
    return rx.dialog.root(
        task_dialog_content(
            task_id,
            on_task_name_edit=on_task_name_edit,
            on_task_description_edit=on_task_description_edit,
            on_assign_milestone=on_assign_milestone,
            on_task_delete=on_delete_task,
        ),
        rx.dialog.trigger(trigger),
        open=State.editing_task_id == task_id,
        on_open_change=lambda e: State.set_editing_task_id(task_id, e),
    )
