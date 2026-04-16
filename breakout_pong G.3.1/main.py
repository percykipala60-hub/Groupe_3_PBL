import flet as ft
import asyncio
from scr.player_VS_player import get_pvp_view
from scr.player_VS_computer import get_pvc_view
from scr.niveaux_choix import niveau_choix_view
from scr.niveaux.Lv1 import get_lv1_view


# --- FONCTION POUR CRÉER BACKGROUND AVEC GRADIENT ---
def create_gradient_background(color1="#87CEEB", color2="#FF4500"):
    """Crée un background avec dégradé personnalisable"""
    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[color1, color2],
        ),
    )


# --- VUE : MENU PRINCIPAL ---
async def main(page: ft.Page):
    page.title = "Breakout Pong"
    page.window.width = 400
    page.window.height = 750
    page.padding = 0
    page.spacing = 0

    # --- FONCTION POUR CRÉER BOUTON AVEC ANIMATION ---
    def create_animated_button(text="", icon=None, on_click=None):
        button_content = ft.Row(
            controls=[
                ft.Icon(name=icon, color="white", size=24) if icon else ft.Container(),
                ft.Text(text, color="white", weight="bold", size=22, italic=True),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
        container = ft.Container(
            content=button_content,
            width=220,
            height=55,
            bgcolor="#E63946",
            border_radius=12,
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.3, "black")
            ),
            scale=1,
            animate_scale=ft.Animation(150, ft.AnimationCurve.DECELERATE),
        )

        def on_down(e):
            container.scale = 0.9
            page.update()

        def on_up(e):
            container.scale = 1.0
            page.update()
            if on_click:
                on_click(e)

        return ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.CLICK,
            on_tap_down=on_down,
            on_tap_up=on_up,
            content=container
        )

    # --- SWITCHERS POUR BOUTONS ---
    btn_1_switcher = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=600,
        switch_in_curve=ft.AnimationCurve.ELASTIC_OUT,
    )
    btn_2_switcher = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=600,
        switch_in_curve=ft.AnimationCurve.ELASTIC_OUT,
    )
    btn_3_switcher = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=600,
        switch_in_curve=ft.AnimationCurve.ELASTIC_OUT,
    )

    # --- BACKGROUND AVEC GRADIENT ---
    background = create_gradient_background()

    # --- LOGO/TITRE ---
    logo_container = ft.Container(
        content=ft.Image(
            src="logo.png",
            width=300,
            height=300,
            fit=ft.ImageFit.CONTAIN,
        ),
        scale=1,
        animate=ft.Animation(800, ft.AnimationCurve.DECELERATE),
        animate_offset=ft.Animation(1000, ft.AnimationCurve.EASE_OUT_BACK),
        offset=ft.Offset(0, 0),
    )

    logo_anime = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=2000,
        switch_in_curve=ft.AnimationCurve.DECELERATE,
    )

    def route_change(route):
        page.views.clear()
        
        # Vue du Menu Principal
        menu_view = ft.View(
            "/",
            controls=[
                ft.Stack(
                    expand=True,
                    controls=[
                        background,
                        ft.Container(
                            content=logo_anime,
                            alignment=ft.alignment.top_center,
                            padding=100
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[btn_1_switcher, btn_2_switcher, btn_3_switcher],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                                tight=True,
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=300),
                        ),
                    ],
                )
            ],
            vertical_alignment="center",
            horizontal_alignment="center",
        )
        page.views.append(menu_view)

        # Gestion des routes additionnelles
        if page.route == "/niveaux":
            page.views.append(niveau_choix_view(page))
        
        if page.route == "/pvp":
            page.views.append(get_pvp_view(page))
        
        if page.route == "/pvc":
            page.views.append(get_pvc_view(page))
        
        if page.route == "/lv1":
            page.views.append(get_lv1_view(page))
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    # --- SÉQUENCE D'ANIMATION ---
    await asyncio.sleep(0.1)
    logo_anime.content = logo_container
    page.update()
    await asyncio.sleep(2)

    logo_container.scale = 1.1
    logo_container.offset = ft.Offset(0, -0.1)
    page.update()
    await asyncio.sleep(1)

    btn_1_switcher.content = create_animated_button(
        text="Choisir Niveau",
        icon=ft.Icons.STAIRS,
        on_click=lambda _: page.go("/niveaux")
    )
    page.update()
    await asyncio.sleep(0.4)

    btn_2_switcher.content = create_animated_button(
        text="Joueur VS Joueur",
        icon=ft.Icons.PEOPLE,
        on_click=lambda _: page.go("/pvp")
    )
    page.update()
    await asyncio.sleep(0.4)

    btn_3_switcher.content = create_animated_button(
        text="Joueur VS CPU",
        icon=ft.Icons.COMPUTER,
        on_click=lambda _: page.go("/pvc")
    )
    page.update()

ft.app(target=main, assets_dir="assets")