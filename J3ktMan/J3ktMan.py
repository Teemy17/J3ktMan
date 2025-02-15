"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from J3ktMan.page.index import index
from J3ktMan.page.signup import signup
from J3ktMan.page.signin import signin


app = rx.App()

app.add_page(index)

# for some reason, the @rx.page(route="...") decorator doesn't work so the route is added manually here :(
app.add_page(signin, route="signin/[[...slug]]")
app.add_page(signup, route="signup/[[...slug]]")
