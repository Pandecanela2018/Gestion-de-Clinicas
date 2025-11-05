import reflex as rx
import asyncio
import httpx # Importar httpx para hacer solicitudes HTTP


class LoginState(rx.State):
    """State for the login form."""

    dui: str = "06915275-9"
    password: str = "Cacahuatique64"
    error_message: str = ""
    is_loading: bool = False
    token: str = rx.Cookie("") # Para almacenar el token de autenticación

    @rx.event
    def handle_login(self, form_data: dict):
        """Handle the login form submission."""
        self.error_message = ""
        self.dui = form_data.get("dui", "")
        self.password = form_data.get("password", "")
        if not self.dui or not self.password:
            self.error_message = "Ambos campos son requeridos."
            self.is_loading = False
        else:
            self.is_loading = True
            yield LoginState.authenticate_user # Llamar a la función de autenticación real

    @rx.event(background=True) # Ejecutar en segundo plano para no bloquear la UI
    async def authenticate_user(self):
        """Autentica al usuario contra el backend de FastAPI."""
        try:
            # URL de tu API de FastAPI (ajusta si es diferente)
            api_url = "http://127.0.0.1:8000/auth/login"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    json={"dui": self.dui, "password": self.password}
                )
                response.raise_for_status() # Lanza una excepción para códigos de estado 4xx/5xx
                
                data = response.json()
                
                async with self: # Actualizar el estado de Reflex de forma segura
                    if "access_token" in data:
                        self.token = data["access_token"] # Almacenar el token
                        self.error_message = ""
                        # Redirigir a una página protegida después del login exitoso
                        yield rx.redirect("/dashboard") # Asumiendo que tienes una página /dashboard
                    else:
                        self.error_message = "Respuesta inesperada del servidor."
            
        except httpx.HTTPStatusError as e:
            async with self:
                if e.response.status_code == 401:
                    self.error_message = "Número de DUI o contraseña incorrectos."
                else:
                    self.error_message = f"Error de servidor: {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            async with self:
                self.error_message = f"Error de red: No se pudo conectar al servidor. {e}"
        except Exception as e:
            async with self:
                self.error_message = f"Ocurrió un error inesperado: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def logout(self):
        """Cierra la sesión del usuario."""
        self.token = "" # Limpiar el token
        yield rx.redirect("/") # Redirigir a la página de login