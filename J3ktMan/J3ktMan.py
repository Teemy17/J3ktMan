"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from J3ktMan.page.index import index
from J3ktMan.page.signup import signup
from J3ktMan.page.signin import signin


app = rx.App()

app.add_page(index)
app.add_page(signin)
app.add_page(signup)
