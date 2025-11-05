import reflex as rx
from components.login_form import login_form


def index() -> rx.Component:
    """The main login page."""
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.image(
                        src="/logosv.jpg",
                        width="128px",
                        height="auto",
                        class_name="mb-12",
                    ),
                    login_form(),
                    class_name="flex flex-col items-center justify-center w-full max-w-md mx-auto",
                ),
                class_name="flex flex-col justify-center w-full lg:w-1/2 min-h-screen px-4 py-12 sm:px-6 lg:px-20 xl:px-24",
            ),
            rx.el.div(
                rx.image(
                    src="/2.png",
                    class_name="w-full h-full object-cover",
                ),
                class_name="hidden lg:block lg:w-1/2 relative h-screen",
            ),
            class_name="flex min-h-screen w-full bg-white",
        ),
        class_name="font-['Inter']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)