import reflex as rx


def bar_chart(data) -> rx.Component:
    return rx.recharts.bar_chart(
        rx.recharts.graphing_tooltip(),
        rx.recharts.bar(
            data_key="count",
            fill=rx.color("accent", 8),
        ),
        rx.recharts.x_axis(data_key="name"),
        rx.recharts.y_axis(
            allow_decimals=False,
        ),
        data=data,
        width="100%",
        height=250,
    )
