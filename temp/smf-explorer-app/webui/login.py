"""Login page and session guard (NiceGUI app.storage.user)."""
from __future__ import annotations

from nicegui import app, run, ui

from app_core import query as query_layer
from app_core.session import SESSIONS, ConnectionFailed, Session

SESSION_KEY = "smf_session_id"


def get_current_session() -> Session | None:
    session_id = app.storage.user.get(SESSION_KEY)
    session = SESSIONS.get(session_id)
    if session is None and session_id is not None:
        app.storage.user.pop(SESSION_KEY, None)
    return session


def require_session() -> Session | None:
    """Returns a live session or redirects to `/login` and returns `None`."""
    session = get_current_session()
    if session is None:
        ui.navigate.to("/login")
        return None
    return session


def logout() -> None:
    session_id = app.storage.user.pop(SESSION_KEY, None)
    if session_id:
        SESSIONS.drop(session_id)
    ui.navigate.to("/login")


def build_connection_string(url: str, username: str, password: str, verify_ssl: bool) -> str:
    """Build dgapi connection string. Rejects `;` in credentials (breaks the delimiter format)."""
    for label, value in (("username", username), ("password", password), ("url", url)):
        if ";" in (value or ""):
            raise ValueError(f"{label} must not contain ';'")
    return (
        f"mode=dgapi;url={url};"
        f"verify_ssl={'true' if verify_ssl else 'false'};"
        f"username={username};password={password}"
    )


def _connect_sync(connection_string: str, dataset_name: str) -> Session:
    """Blocking connect + dataset validate + discover — run via io_bound."""
    session = SESSIONS.create(connection_string, dataset_name)
    try:
        ctx = session.environment.new_context(dataset_name)
        ctx.get_dataset_description()
        session.contexts[dataset_name] = ctx
        query_layer.refresh_available(session)
    except Exception:
        SESSIONS.drop(session.session_id)
        raise
    return session


def register_login_page() -> None:
    @ui.page("/login")
    def login_page() -> None:
        if get_current_session() is not None:
            ui.navigate.to("/")
            return

        ui.dark_mode(True)

        with ui.card().classes("absolute-center w-96"):
            ui.label("SMF Explorer — sign in").classes("text-lg font-bold")
            ui.label(
                "Enter the z/OS Data Gatherer address (mock or real machine) — "
                "the form works identically for both."
            ).classes("text-sm text-grey-5")

            url = ui.input(
                "Connection URL",
                placeholder="http://127.0.0.1:9000/zosmf/zosdg/smf",
            ).classes("w-full")
            username = ui.input("Username").classes("w-full")
            password = ui.input("Password", password=True, password_toggle_button=True).classes("w-full")
            verify_ssl = ui.checkbox("Verify TLS", value=False)
            tls_warn = ui.label(
                "TLS verification is off — credentials may be exposed on the network."
            ).classes("text-xs text-orange-6")
            tls_warn.bind_visibility_from(verify_ssl, "value", backward=lambda v: not v)

            dataset_name = ui.input(
                "Dataset name",
                placeholder="TEST.SMF.DATASET",
            ).classes("w-full")

            status = ui.label("").classes("text-negative")

            async def do_login() -> None:
                if not url.value or not dataset_name.value:
                    status.text = "Please provide at least Connection URL and Dataset name."
                    return

                status.text = ""
                try:
                    connection_string = build_connection_string(
                        url.value, username.value or "", password.value or "", bool(verify_ssl.value)
                    )
                except ValueError as exc:
                    status.text = str(exc)
                    return

                login_button.props("loading")
                try:
                    session = await run.io_bound(_connect_sync, connection_string, dataset_name.value)
                except ConnectionFailed:
                    status.text = "Connection failed. Check URL, credentials, and network."
                    return
                except Exception:
                    status.text = "Could not open the dataset. Check the dataset name and permissions."
                    return
                finally:
                    login_button.props(remove="loading")

                app.storage.user[SESSION_KEY] = session.session_id
                ui.notify(
                    f"Connected — {len(session.available)} SMF type(s) in dataset",
                    type="positive",
                )
                ui.navigate.to("/")

            login_button = ui.button("Connect", on_click=do_login).classes("w-full mt-2")
