import flet as ft
import random
import asyncio
import time

WIDTH = 400
HEIGHT = 700
PADDLE_WIDTH = 120
PADDLE_HEIGHT = 12
BALL_SIZE = 12
SPEED = 5

# 🎨 Couleurs Néon
NEON_CYAN = "#00D9FF"
NEON_MAGENTA = "#FF00FF"
NEON_PINK = "#FF006E"
NEON_GREEN = "#39FF14"
NEON_PURPLE = "#B700FF"

def get_pvp_view(page: ft.Page):
    # --- LOGIQUE DU JEU ---
    ball_x = WIDTH / 2
    ball_y = HEIGHT / 2
    ball_prev_x = ball_x
    ball_prev_y = ball_y
    dx = 0
    dy = 0

    paddle_bottom_x = WIDTH / 2 - PADDLE_WIDTH / 2
    paddle_top_x = WIDTH / 2 - PADDLE_WIDTH / 2
    paddle_bottom_vel = 0
    paddle_top_vel = 0
    
    keys_pressed = {}
    last_frame_time = time.time()
    elapsed_time = 0
    
    score_top = 0
    score_bottom = 0
    last_paddle_hit = None
    is_paused = False
    game_started = False
    game_finished = False
    current_speed = SPEED
    speed_increased = False
    match_duration = 3 * 60  # 3 minutes par défaut

    # --- COMPOSANTS GRAPHIQUES ---
    ball = ft.Container(
        width=BALL_SIZE, height=BALL_SIZE, bgcolor=NEON_CYAN,
        border_radius=6, left=ball_x, top=ball_y,
        shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN)
    )

    paddle_bottom = ft.Container(
        width=PADDLE_WIDTH, height=PADDLE_HEIGHT, bgcolor=NEON_MAGENTA,
        left=paddle_bottom_x, top=HEIGHT - 60,
        shadow=ft.BoxShadow(blur_radius=15, color=NEON_MAGENTA)
    )

    paddle_top = ft.Container(
        width=PADDLE_WIDTH, height=PADDLE_HEIGHT, bgcolor=NEON_PINK,
        left=paddle_top_x, top=40,
        shadow=ft.BoxShadow(blur_radius=15, color=NEON_PINK)
    )

    score_text_top = ft.Text(value="0", size=60, color=NEON_PINK, weight="bold")
    score_text_bottom = ft.Text(value="0", size=60, color=NEON_MAGENTA, weight="bold")
    time_text_top = ft.Text(value="0:00", size=16, color=NEON_PINK, weight="bold")
    time_text_bottom = ft.Text(value="0:00", size=16, color=NEON_MAGENTA, weight="bold")

    countdown_text = ft.Text(value="3", size=120, color=NEON_GREEN, text_align=ft.TextAlign.CENTER, weight="bold")
    countdown_container = ft.Container(
        content=countdown_text, width=WIDTH, height=HEIGHT,
        bgcolor=None, alignment=ft.alignment.center, left=0, top=0,
    )

    stats_container_top = ft.Container(
        content=ft.Column([score_text_top, time_text_top], alignment="center", horizontal_alignment="center", spacing=5),
        width=150, height=100, left=WIDTH / 2 - 75, top=HEIGHT / 4 - 50,
    )

    stats_container_bottom = ft.Container(
        content=ft.Column([time_text_bottom, score_text_bottom], alignment="center", horizontal_alignment="center", spacing=5),
        width=150, height=100, left=WIDTH / 2 - 75, top=3 * HEIGHT / 4 - 50,
    )

    border_top = ft.Container(width=WIDTH, height=2, bgcolor=NEON_CYAN, left=0, top=0, shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN))
    border_bottom = ft.Container(width=WIDTH, height=2, bgcolor=NEON_CYAN, left=0, top=HEIGHT - 2, shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN))
    border_left = ft.Container(width=2, height=HEIGHT, bgcolor=NEON_CYAN, left=0, top=0, shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN))
    border_right = ft.Container(width=2, height=HEIGHT, bgcolor=NEON_CYAN, left=WIDTH - 2, top=0, shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN))
    border_middle = ft.Container(width=WIDTH, height=2, bgcolor=NEON_CYAN, left=0, top=HEIGHT / 2, shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN))

    # 🏆 Écran Fin de Match
    result_text_top = ft.Text(value="", size=80, color=NEON_GREEN, weight="bold", italic=True, text_align=ft.TextAlign.CENTER)
    result_text_bottom = ft.Text(value="", size=80, color=NEON_GREEN, weight="bold", italic=True, text_align=ft.TextAlign.CENTER)
    final_score = ft.Text(value="", size=24, color="white", weight="bold", text_align=ft.TextAlign.CENTER)
    
    game_over_screen = ft.Container(
        content=ft.Column([
            ft.Container(height=60),
            result_text_top,
            ft.Container(height=30),
            final_score,
            ft.Container(height=30),
            result_text_bottom,
            ft.Container(height=60),
            ft.ElevatedButton(
                "Retour au menu",
                on_click=lambda _: page.go("/"),
                style=ft.ButtonStyle(
                    bgcolor={"": NEON_MAGENTA},
                    color={"": "white"}
                )
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
        width=WIDTH, height=HEIGHT,
        bgcolor=ft.Colors.with_opacity(0.95, "black"),
        visible=False, left=0, top=0
    )

    # 🎯 Écran Sélection Durée
    def set_duration(minutes):
        nonlocal match_duration
        match_duration = minutes * 60
        duration_screen.visible = False
        page.update()
        page.run_task(game_loop)

    duration_screen = ft.Container(
        content=ft.Column([
            ft.Text("DURÉE DU MATCH", size=28, color=NEON_GREEN, weight="bold", italic=True, text_align=ft.TextAlign.CENTER),
            ft.Container(height=40),
            ft.ElevatedButton(
                "1 minute",
                on_click=lambda _: set_duration(1),
                width=200,
                style=ft.ButtonStyle(bgcolor={"": NEON_MAGENTA}, color={"": "white"})
            ),
            ft.ElevatedButton(
                "3 minutes",
                on_click=lambda _: set_duration(3),
                width=200,
                style=ft.ButtonStyle(bgcolor={"": NEON_MAGENTA}, color={"": "white"})
            ),
            ft.ElevatedButton(
                "5 minutes",
                on_click=lambda _: set_duration(5),
                width=200,
                style=ft.ButtonStyle(bgcolor={"": NEON_MAGENTA}, color={"": "white"})
            ),
            ft.ElevatedButton(
                "10 minutes",
                on_click=lambda _: set_duration(10),
                width=200,
                style=ft.ButtonStyle(bgcolor={"": NEON_MAGENTA}, color={"": "white"})
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        width=WIDTH, height=HEIGHT,
        bgcolor=ft.Colors.with_opacity(0.95, "black"),
        visible=True, left=0, top=0
    )

    def toggle_pause(e):
        nonlocal is_paused
        is_paused = not is_paused
        pause_btn.icon = ft.Icons.PLAY_ARROW if is_paused else ft.Icons.PAUSE
        page.update()

    pause_btn = ft.IconButton(icon=ft.Icons.PAUSE, icon_color=NEON_GREEN, on_click=toggle_pause)
    pause_container = ft.Container(content=pause_btn, left=10, top=HEIGHT / 2 - 20)

    game_stack = ft.Stack(
        width=WIDTH, height=HEIGHT,
        controls=[
            border_top, border_bottom, border_left, border_right, border_middle,
            stats_container_top, stats_container_bottom, pause_container,
            ball, paddle_bottom, paddle_top, countdown_container,
            game_over_screen, duration_screen,
        ],
    )

    # Création de la View de retour
    view = ft.View(
        "/pvp",
        bgcolor="black",
        padding=0,
        controls=[
            game_stack,
            ft.TextButton("QUITTER", on_click=lambda _: page.go("/"), style=ft.ButtonStyle(color=NEON_CYAN))
        ]
    )

    # --- ÉVÉNEMENTS CLAVIER NATIFS ET MANETTES ---
    import ctypes
    def is_key_pressed(vk):
        return (ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000) != 0
    VK_LEFT, VK_RIGHT, VK_A, VK_D = 0x25, 0x27, 0x41, 0x44

    gp_state = {"p1_left": False, "p1_right": False, "p2_left": False, "p2_right": False}

    # --- SUPPORT MANETTES (pygame) avec assignation dynamique ---
    import threading
    try:
        import pygame as _pygame
        
        def _gamepad_loop():
            _pygame.init()
            _pygame.joystick.init()
            _joysticks = {}
            assigned_joysticks = {"p1": None, "p2": None}
            assign_cooldown = 0

            # Enregistrer les manettes déjà connectées
            for i in range(_pygame.joystick.get_count()):
                j = _pygame.joystick.Joystick(i)
                j.init()
                _joysticks[j.get_instance_id()] = j

            while True:
                try:
                    # Gestion propre des déconnexions/reconnexions (hotplug)
                    for event in _pygame.event.get():
                        if event.type == _pygame.JOYDEVICEADDED:
                            j = _pygame.joystick.Joystick(event.device_index)
                            j.init()
                            _joysticks[j.get_instance_id()] = j
                        elif event.type == _pygame.JOYDEVICEREMOVED:
                            if event.instance_id in _joysticks:
                                j = _joysticks[event.instance_id]
                                j.quit()
                                del _joysticks[event.instance_id]
                                # Libérer l'assignation si la manette se déconnecte
                                if assigned_joysticks["p1"] == event.instance_id: assigned_joysticks["p1"] = None
                                if assigned_joysticks["p2"] == event.instance_id: assigned_joysticks["p2"] = None

                    # Lecture et assignation des manettes
                    for iid, j in _joysticks.items():
                        ax = j.get_axis(0) if j.get_numaxes() > 0 else 0
                        hat = j.get_hat(0) if j.get_numhats() > 0 else (0, 0)
                        left_x = ax if abs(ax) > 0.25 else float(hat[0])

                        is_moving = abs(left_x) > 0.25

                        # Assignation dynamique de la manette au joueur dès le premier mouvement
                        if is_moving:
                            now = time.time()
                            if assigned_joysticks["p1"] is None and assigned_joysticks["p2"] != iid:
                                assigned_joysticks["p1"] = iid
                                assign_cooldown = now + 1.0
                            elif assigned_joysticks["p2"] is None and assigned_joysticks["p1"] != iid:
                                if now < assign_cooldown:
                                    continue
                                # Protection Anti-Clone absolue :
                                # La manette 2 s'assigne uniquement si la manette 1 est au repos.
                                p1_is_moving = False
                                p1_iid = assigned_joysticks["p1"]
                                if p1_iid is not None and p1_iid in _joysticks:
                                    p1_j = _joysticks[p1_iid]
                                    p1_ax = p1_j.get_axis(0) if p1_j.get_numaxes() > 0 else 0
                                    p1_hat = p1_j.get_hat(0) if p1_j.get_numhats() > 0 else (0, 0)
                                    p1_is_moving = abs(p1_ax) > 0.25 or abs(p1_hat[0]) > 0
                                
                                if p1_is_moving:
                                    continue  # Le clone agit pendant que P1 bouge, on l'esquive
                                    
                                assigned_joysticks["p2"] = iid

                        # Appliquer la commande en fonction de l'assignation
                        if assigned_joysticks["p1"] == iid:
                            gp_state["p1_left"]  = left_x < -0.25
                            gp_state["p1_right"] = left_x > 0.25
                        elif assigned_joysticks["p2"] == iid:
                            gp_state["p2_left"] = left_x < -0.25
                            gp_state["p2_right"] = left_x > 0.25

                except Exception:
                    pass
                time.sleep(0.016)

        threading.Thread(target=_gamepad_loop, daemon=True).start()
    except ImportError:
        pass  # pygame non installé, utiliser clavier uniquement

    def move_bottom(e: ft.DragUpdateEvent):
        nonlocal paddle_bottom_x, paddle_bottom_vel
        paddle_bottom_x += e.delta_x
        paddle_bottom_vel = e.delta_x
        paddle_bottom.left = max(0, min(WIDTH - PADDLE_WIDTH, paddle_bottom_x))
        page.update()

    def move_top(e: ft.DragUpdateEvent):
        nonlocal paddle_top_x, paddle_top_vel
        paddle_top_x += e.delta_x
        paddle_top_vel = e.delta_x
        paddle_top.left = max(0, min(WIDTH - PADDLE_WIDTH, paddle_top_x))
        page.update()

    paddle_bottom.on_pan_update = move_bottom
    paddle_top.on_pan_update = move_top

    def reset_ball(scorer=None):
        nonlocal ball_x, ball_y, dx, dy, score_top, score_bottom, current_speed, speed_increased
        current_speed = SPEED
        speed_increased = False
        if scorer == "top":
            score_top += 1
            score_text_top.value = str(score_top)
            dy = -current_speed
        elif scorer == "bottom":
            score_bottom += 1
            score_text_bottom.value = str(score_bottom)
            dy = current_speed
        else:
            dy = random.choice([-current_speed, current_speed])
        dx = random.choice([-1, 0, 1])
        ball_x = WIDTH / 2
        ball_y = HEIGHT / 2

    def update_game(delta_time):
        nonlocal ball_x, ball_y, ball_prev_x, ball_prev_y, dx, dy, paddle_bottom_x, paddle_top_x, current_speed, speed_increased, last_paddle_hit
        if not game_started: return

        if elapsed_time >= 5 and not speed_increased:
            current_speed = SPEED * 1.3
            speed_increased = True
            if dy != 0: dy = (dy / abs(dy)) * current_speed

        # Clavier + Manette
        key_speed = 10
        if is_key_pressed(VK_LEFT) or gp_state["p1_left"]: paddle_bottom_x = max(0, paddle_bottom_x - key_speed)
        if is_key_pressed(VK_RIGHT) or gp_state["p1_right"]: paddle_bottom_x = min(WIDTH - PADDLE_WIDTH, paddle_bottom_x + key_speed)
        if is_key_pressed(VK_A) or gp_state["p2_left"]: paddle_top_x = max(0, paddle_top_x - key_speed)
        if is_key_pressed(VK_D) or gp_state["p2_right"]: paddle_top_x = min(WIDTH - PADDLE_WIDTH, paddle_top_x + key_speed)

        paddle_bottom.left = max(0, min(WIDTH - PADDLE_WIDTH, paddle_bottom_x))
        paddle_top.left = max(0, min(WIDTH - PADDLE_WIDTH, paddle_top_x))

        ball_prev_y = ball_y
        ball_x += dx
        ball_y += dy

        # Rebond murs latéraux avec clampage strict
        if ball_x <= 0:
            ball_x = 1
            dx = abs(dx)
        elif ball_x >= WIDTH - BALL_SIZE:
            ball_x = WIDTH - BALL_SIZE - 1
            dx = -abs(dx)

        # Collision raquette bas (anti-stuck)
        if (dy > 0 and ball_y + BALL_SIZE >= paddle_bottom.top
                and paddle_bottom.left <= ball_x <= paddle_bottom.left + PADDLE_WIDTH):
            # Calcul de l'angle basé sur le point d'impact
            paddle_center = paddle_bottom.left + PADDLE_WIDTH / 2
            ball_center = ball_x + BALL_SIZE / 2
            relative_intersect_x = ball_center - paddle_center
            normalized_intersect_x = relative_intersect_x / (PADDLE_WIDTH / 2)
            
            dx = normalized_intersect_x * (current_speed * 1.5)
            dy = -abs(dy)
            ball_y = paddle_bottom.top - BALL_SIZE

        # Collision raquette haut (anti-stuck)
        if (dy < 0 and ball_y <= paddle_top.top + PADDLE_HEIGHT
                and paddle_top.left <= ball_x <= paddle_top.left + PADDLE_WIDTH):
            # Calcul de l'angle basé sur le point d'impact
            paddle_center = paddle_top.left + PADDLE_WIDTH / 2
            ball_center = ball_x + BALL_SIZE / 2
            relative_intersect_x = ball_center - paddle_center
            normalized_intersect_x = relative_intersect_x / (PADDLE_WIDTH / 2)
            
            dx = normalized_intersect_x * (current_speed * 1.5)
            dy = abs(dy)
            ball_y = paddle_top.top + PADDLE_HEIGHT

        if ball_y <= 0: reset_ball("bottom")
        elif ball_y >= HEIGHT: reset_ball("top")

        ball.left = ball_x
        ball.top = ball_y

    async def game_loop():
        nonlocal elapsed_time, game_started, last_frame_time, game_finished
        for i in range(3, 0, -1):
            countdown_text.value = str(i)
            page.update()
            await asyncio.sleep(1)
        countdown_text.value = "GO!"
        page.update()
        await asyncio.sleep(0.5)
        countdown_container.visible = False
        game_started = True
        last_frame_time = time.time()
        reset_ball()
        
        # La boucle s'arrête si on quitte la route /pvp
        while page.route == "/pvp" and not game_finished:
            curr = time.time()
            dt = curr - last_frame_time
            last_frame_time = curr
            if not is_paused:
                update_game(dt)
                elapsed_time += dt
                ts = f"{int(elapsed_time)//60}:{int(elapsed_time)%60:02d}"
                time_text_top.value = time_text_bottom.value = ts
                
                # Vérifier si le temps est écoulé
                if elapsed_time >= match_duration:
                    game_finished = True
                    # Déterminer le gagnant
                    if score_top > score_bottom:
                        result_text_top.value = "WIN"
                        result_text_bottom.value = "LOSE"
                        result_text_top.color = NEON_GREEN
                        result_text_bottom.color = NEON_PINK
                    elif score_bottom > score_top:
                        result_text_top.value = "LOSE"
                        result_text_bottom.value = "WIN"
                        result_text_top.color = NEON_PINK
                        result_text_bottom.color = NEON_GREEN
                    else:
                        result_text_top.value = "DRAW"
                        result_text_bottom.value = "DRAW"
                        result_text_top.color = NEON_CYAN
                        result_text_bottom.color = NEON_CYAN
                    
                    final_score.value = f"{int(score_top)} - {int(score_bottom)}"
                    game_over_screen.visible = True
                    
            page.update()
            await asyncio.sleep(0.016)

    page.run_task(game_loop)
    return view