import reflex as rx
from states.login_state import LoginState


def form_field(
    label: str, placeholder: str, field_name: str, field_type: str
) -> rx.Component:
    """A reusable form field component."""
    return rx.el.div(
        rx.el.label(
            label,
            html_for=field_name,
            class_name="block text-sm font-medium text-gray-700 mb-1",
        ),
        rx.el.input(
            id=field_name,
            name=field_name,
            placeholder=placeholder,
            type=field_type,
            on_change=LoginState.set_error_message(""),
            class_name="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-shadow",
        ),
        class_name="w-full",
    )


def login_form() -> rx.Component:
    """The login form component."""
    return rx.el.div(
        rx.el.h1("Iniciar Sesión", class_name="text-4xl font-bold text-gray-800 mb-2"),
        rx.el.p(
            "Bienvenido de nuevo. Ingrese sus credenciales.",
            class_name="text-gray-500 mb-8",
        ),
        rx.el.form(
            rx.el.div(
                form_field(
                    label="Número de DUI",
                    placeholder="00000000-0",
                    field_name="dui",
                    field_type="text",
                ),
                form_field(
                    label="Contraseña",
                    placeholder="********",
                    field_name="password",
                    field_type="password",
                ),
                rx.cond(
                    LoginState.error_message != "",
                    rx.el.div(
                        rx.icon("badge_alert", class_name="w-5 h-5 mr-2"),
                        rx.el.span(LoginState.error_message),
                        class_name="flex items-center bg-red-100 text-red-600 p-3 rounded-lg text-sm",
                    ),
                ),
                rx.el.button(
                    rx.cond(
                        LoginState.is_loading,
                        rx.spinner(class_name="text-white"),
                        rx.el.span("Iniciar Sesión"),
                    ),
                    type="submit",
                    disabled=LoginState.is_loading,
                    class_name="w-full bg-violet-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-violet-500 transition-colors flex justify-center items-center h-12",
                ),
                rx.el.div(
                    rx.el.a(
                        "¿Has olvidado tu contraseña?",
                        href="#",
                        class_name="text-sm font-medium text-violet-600 hover:text-violet-500 hover:underline",
                    ),
                    class_name="text-center mt-4",
                ),
                class_name="flex flex-col gap-6",
            ),
            on_submit=LoginState.handle_login,
        ),
        class_name="w-full max-w-md bg-white p-8 md:p-12 rounded-2xl shadow-xl border border-gray-100",
    )