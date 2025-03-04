import reflex as rx

data01 = [
    {"name": "Group A", "value": 400},
    {"name": "Group B", "value": 300},
    {"name": "Group C", "value": 300},
    {"name": "Group D", "value": 200},
    {"name": "Group E", "value": 278},
    {"name": "Group F", "value": 189},
]
data02 = [
    {"name": "Group A", "value": 2400},
    {"name": "Group B", "value": 4567},
    {"name": "Group C", "value": 1398},
    {"name": "Group D", "value": 9800},
    {"name": "Group E", "value": 3908},
    {"name": "Group F", "value": 4800},
]

def pie_chart() -> rx.Component:
    return rx.recharts.pie_chart(
            rx.recharts.pie(
                data=data01,
                data_key="value",
                name_key="name",
                fill="#82ca9d",
                inner_radius="60%",
                padding_angle=5,
            ),
            rx.recharts.pie(
                data=data02,
                data_key="value",
                name_key="name",
                fill="#8884d8",
                outer_radius="50%",
            ),
            rx.recharts.graphing_tooltip(),
            width="100%",
            height=300,
    )
