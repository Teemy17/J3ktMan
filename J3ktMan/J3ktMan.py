"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from J3ktMan.page.index import index
from J3ktMan.page.join_project import join_project
from J3ktMan.page.signup import signup
from J3ktMan.page.signin import signin
from J3ktMan.page.home import home

# the following import is necessary to register the model with the database
from J3ktMan.model import project  # noqa


app = rx.App()

app.add_page(index)

# for some reason, the @rx.page(route="...") decorator doesn't work so the route is added manually here :(
app.add_page(signin, route="signin/[[...slug]]")
app.add_page(signup, route="signup/[[...slug]]")
app.add_page(home, route="home/[[...slug]]")

app.add_page(join_project)
