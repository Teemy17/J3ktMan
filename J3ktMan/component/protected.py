from reflex_clerk import ClerkState
from reflex.event import EventSpec, EventType

import reflex_clerk as clerk
import reflex as rx


from J3ktMan.secret.clerk import PUBLISHABLE_KEY, SECRET_KEY


class Redirect(rx.State):
    @rx.event
    async def redirect(self) -> EventSpec | None:
        return rx.redirect(
            f"/signin?redirect_url={self.router.page.full_raw_path}"
        )


class Protected(rx.Component):
    tag = "J3ktManProtected"

    on_render: rx.EventHandler[lambda: []]

    def add_imports(
        self,
    ) -> rx.ImportDict | list[rx.ImportDict]:
        return {
            "@clerk/clerk-react": ["useAuth"],
            "react": ["useContext", "useEffect"],
            "/utils/context": ["EventLoopContext"],
            "/utils/state": ["Event"],
        }

    def add_custom_code(self) -> list[str]:
        return [
            """
function J3ktManProtected({ children }) {
  const { getToken, isLoaded, isSignedIn } = useAuth()
  const [ addEvents, connectErrors ] = useContext(EventLoopContext)

  useEffect(() => {
      if (isLoaded && !!addEvents) {
        if (!isSignedIn) {
          addEvents([Event("%s.redirect")])
        }
      }
  }, [isSignedIn])      

  return (
      <>{children}</>
  )
}
            """
            % (Redirect.get_full_name())
        ]

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        return super().create(
            rx.cond(
                ClerkState.is_signed_in,
                rx.fragment(*children),
                rx.center(rx.spinner(size="3"), height="100vh"),
            ),
            **props,
        )


protected = Protected.create
"""
Wraps a component that requires the clerk user to be signed in. If the user is 
not signed in, the user will be redirected to the sign in page.

## Note

The component requires the `clerk_provider` to be used in the parent component.
"""


def protected_page_with(
    on_signed_in: EventType[()] | None = None,
    on_signed_out: EventType[()] | None = None,
):
    """
    A decorator that wraps a page function to require the clerk user to be
    signed in.

    If the user is not signed in, the user will be redirected to the sign in
    page.

    The component will be wrapped in a `clerk_provider` component, therefore,
    there should not be any `clerk_provider` in the component.
    """

    def dectorator(render_fn):
        def wrapper(*args, **kwargs):
            return clerk.clerk_provider(
                protected(render_fn(*args, **kwargs)),
                publishable_key=PUBLISHABLE_KEY,
                secret_key=SECRET_KEY,
                on_signed_in=on_signed_in,
                on_signed_out=on_signed_out,
            )

        wrapper.__name__ = render_fn.__name__

        return wrapper

    return dectorator


def protected_page(func):
    """
    A decorator that wraps a page function to require the clerk user to be
    signed in.

    If the user is not signed in, the user will be redirected to the sign in
    page.

    The component will be wrapped in a `clerk_provider` component, therefore,
    there should not be any `clerk_provider` in the component.
    """

    def wrapper(*args, **kwargs):
        return clerk.clerk_provider(
            protected(func(*args, **kwargs)),
            publishable_key=PUBLISHABLE_KEY,
            secret_key=SECRET_KEY,
        )

    wrapper.__name__ = func.__name__

    return wrapper
