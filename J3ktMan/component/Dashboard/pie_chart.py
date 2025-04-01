import reflex as rx


def pie_chart(data=None) -> rx.Component:
    return rx.recharts.pie_chart(
        rx.recharts.pie(
            data=data,
            data_key="value",
            name_key="name",
            cx="50%",
            cy="50%",
            label=True,
            label_line=True,
            outer_radius="80%",
        ),
        rx.recharts.graphing_tooltip(),
        rx.recharts.legend(),
        width="100%",
        height=250,
    )
