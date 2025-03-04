import reflex as rx

data = [
    {"name": "Low", "uv": 1},
    {"name": "Medium", "uv": 2},
    {"name": "High", "uv": 0},
]

def bar_chart() -> rx.Component:
    return rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="uv",
                stroke=rx.color("accent", 9),
                fill=rx.color("accent", 8),
            ),
            rx.recharts.x_axis(data_key="name"),
            rx.recharts.y_axis(),
            data=data,
            width="100%",
            height=250,
        )
