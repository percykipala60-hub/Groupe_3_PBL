import flet as ft

def niveau_choix_view(page: ft.Page):
    def level_button(level, enabled=False):
        return ft.Container(
            width=60, height=60, border_radius=12,
            alignment=ft.Alignment.center,
            bgcolor="#1E3A8A" if enabled else "#1E293B",
            border=ft.Border.all(2, "#38BDF8" if enabled else "#334155"),
            content=ft.Text(str(level), size=20, color="white" if enabled else "#64748B", weight="bold"),
            on_click=lambda _: page.go("/lv1") if level == 1 else None
        )

    return ft.View(
        "/niveaux",
        controls=[
            ft.AppBar(title=ft.Text("SÉLECTION DU NIVEAU"), bgcolor="#1E3A8A"),
            ft.Column(
                horizontal_alignment="center",
                spacing=20,
                controls=[
                    ft.Row(
                        alignment="center",
                        spacing=15,
                        controls=[level_button(1, True), level_button(2), level_button(3)],
                    ),
                    ft.TextButton("RETOUR AU MENU", on_click=lambda _: page.go("/")),
                ],
            )
        ],
        vertical_alignment="center",
        horizontal_alignment="center",
    )
            