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
MAX_SPEED = 16

# 🎨 Couleurs Néon
NEON_CYAN = "#00D9FF"
NEON_MAGENTA = "#FF00FF"
NEON_PINK = "#FF006E"
NEON_GREEN = "#39FF14"
NEON_PURPLE = "#B700FF"

difficulty = "medium"

def get_ai_settings():
    if difficulty == "easy":
        return {"speed": 5.5, "error": 20, "reaction": 0.1, "ball_speed": 8}
    elif difficulty == "hard":
        return {"speed": 11.5, "error": 2, "reaction": 0.0, "ball_speed": 13}
    elif difficulty == "impossible":
        return {"speed": 16.0, "error": 0, "reaction": 0.0, "ball_speed": 18}
    else:
        return {"speed": 8.0, "error": 8, "reaction": 0.02, "ball_speed": 10}

def get_pvc_view(page: ft.Page):
    # --- LOGIQUE DU JEU ---
    ball_x = WIDTH / 2
    ball_y = HEIGHT / 2
    ball_prev_x = ball_x
    ball_prev_y = ball_y
    dx = 0
    dy = 0

    paddle_bottom_x = WIDTH / 2 - PADDLE_WIDTH / 2
    paddle_top_x = WIDTH / 2 - PADDLE_WIDTH / 2
    
    last_frame_time = time.time()
    elapsed_time = 0
    
    score_top = 0      # CPU Score
    score_bottom = 0   # Player Score
    
    is_paused = False
    game_started = False
    game_finished = False
    current_speed = SPEED
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
        visible=False
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

    # 🎯 Écrans de Sélection
    def set_duration(minutes):
        nonlocal match_duration
        match_duration = minutes * 60
        duration_screen.visible = False
        game_stack.visible = True
        page.update()
        page.run_task(game_loop)

    duration_screen = ft.Container(
        content=ft.Column([
            ft.Text("DURÉE DU MATCH", size=28, color=NEON_GREEN, weight="bold", italic=True, text_align=ft.TextAlign.CENTER),
            ft.Container(height=40),
            ft.ElevatedButton("1 minute", on_click=lambda _: set_duration(1), width=200, style=ft.ButtonStyle(bgcolor={"": NEON_MAGENTA}, color={"": "white"})),
            ft.ElevatedButton("3 minutes", on_click=lambda _: set_duration(3), width=200, style=ft.ButtonStyle(bgcolor={"": NEON_MAGENTA}, color={"": "white"})),
            ft.ElevatedButton("5 minutes", on_click=lambda _: set_duration(5), width=200, style=ft.ButtonStyle(bgcolor={"": NEON_MAGENTA}, color={"": "white"})),
            ft.ElevatedButton("10 minutes", on_click=lambda _: set_duration(10), width=200, style=ft.ButtonStyle(bgcolor={"": NEON_MAGENTA}, color={"": "white"})),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        width=WIDTH, height=HEIGHT,
        bgcolor=ft.Colors.with_opacity(0.95, "black"),
        visible=False, left=0, top=0
    )

    def set_diff(diff):
        global difficulty
        difficulty = diff
        diff_screen.visible = False
        duration_screen.visible = True
        page.update()

    diff_screen = ft.Container(
        content=ft.Column([
            ft.Text("DIFFICULTÉ", size=28, color=NEON_GREEN, weight="bold", italic=True, text_align=ft.TextAlign.CENTER),
            ft.Container(height=40),
            ft.ElevatedButton("Facile", on_click=lambda _: set_diff("easy"), width=200, style=ft.ButtonStyle(bgcolor={"": "#E63946"}, color={"": "white"})),
            ft.ElevatedButton("Moyen", on_click=lambda _: set_diff("medium"), width=200, style=ft.ButtonStyle(bgcolor={"": "#E63946"}, color={"": "white"})),
            ft.ElevatedButton("Difficile", on_click=lambda _: set_diff("hard"), width=200, style=ft.ButtonStyle(bgcolor={"": "#E63946"}, color={"": "white"})),
            ft.ElevatedButton("IMPOSSIBLE", on_click=lambda _: set_diff("impossible"), width=200, style=ft.ButtonStyle(bgcolor={"": NEON_PURPLE}, color={"": "white"})),
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
            game_over_screen, diff_screen, duration_screen,
        ],
        visible=True
    )

    # --- ÉVÉNEMENTS CLAVIER NATIFS (Windows) ---
    import ctypes
    def is_key_pressed(vk):
        return (ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000) != 0
    VK_LEFT, VK_RIGHT = 0x25, 0x27

    def move_bottom(e: ft.DragUpdateEvent):
        nonlocal paddle_bottom_x
        paddle_bottom_x += e.delta_x
        paddle_bottom.left = max(0, min(WIDTH - PADDLE_WIDTH, paddle_bottom_x))
        page.update()

    paddle_bottom.on_pan_update = move_bottom

    def reset_ball(scorer=None):
        nonlocal ball_x, ball_y, dx, dy, score_top, score_bottom, current_speed
        settings = get_ai_settings()
        current_speed = settings["ball_speed"]
        if scorer == "top": # CPU Mark
            score_top += 1
            score_text_top.value = str(score_top)
            dy = -current_speed
        elif scorer == "bottom": # Player Mark
            score_bottom += 1
            score_text_bottom.value = str(score_bottom)
            dy = current_speed
        else:
            dy = random.choice([-current_speed, current_speed])
        
        dx = random.choice([-2, 2])
        ball_x = WIDTH / 2
        ball_y = HEIGHT / 2

    def update_game(dt):
        nonlocal ball_x, ball_y, ball_prev_x, ball_prev_y, dx, dy, paddle_bottom_x, paddle_top_x, current_speed
        if not game_started or game_finished: return

        # Update Speed with time
        settings = get_ai_settings()
        multiplier = min(1 + elapsed_time / 15, 2.5)
        current_speed = min(settings["ball_speed"] * multiplier, MAX_SPEED)
        if dy != 0: dy = (dy / abs(dy)) * current_speed

        # Player Logic (Keyboard)
        key_speed = 10
        if is_key_pressed(VK_LEFT): paddle_bottom_x = max(0, paddle_bottom_x - key_speed)
        if is_key_pressed(VK_RIGHT): paddle_bottom_x = min(WIDTH - PADDLE_WIDTH, paddle_bottom_x + key_speed)
        paddle_bottom.left = paddle_bottom_x

        # AI Logic
        if ball_y < HEIGHT / 2:
            target = ball_x + random.randint(-settings["error"], settings["error"])
            if target > paddle_top_x + PADDLE_WIDTH/2: paddle_top_x += settings["speed"]
            else: paddle_top_x -= settings["speed"]
        paddle_top.left = max(0, min(WIDTH - PADDLE_WIDTH, paddle_top_x))

        ball_prev_y = ball_y
        ball_x += dx
        ball_y += dy

        # Rebond murs latéraux
        if ball_x <= 0:
            ball_x = 1
            dx = abs(dx)
        elif ball_x >= WIDTH - BALL_SIZE:
            ball_x = WIDTH - BALL_SIZE - 1
            dx = -abs(dx)

        # Collision raquette bas (avec anti-stuck)
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

        # Collision raquette haut (avec anti-stuck)
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
        
        countdown_container.visible = True
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
        
        while page.route == "/pvc" and not game_finished:
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
                    if score_bottom > score_top:
                        result_text_bottom.value = "WIN"
                        result_text_top.value = "LOSE"
                        result_text_bottom.color = NEON_GREEN
                        result_text_top.color = NEON_PINK
                    elif score_top > score_bottom:
                        result_text_bottom.value = "LOSE"
                        result_text_top.value = "WIN"
                        result_text_bottom.color = NEON_PINK
                        result_text_top.color = NEON_GREEN
                    else:
                        result_text_top.value = "DRAW"
                        result_text_bottom.value = "DRAW"
                        result_text_top.color = NEON_CYAN
                        result_text_bottom.color = NEON_CYAN
                    
                    final_score.value = f"{int(score_bottom)} - {int(score_top)}"
                    game_over_screen.visible = True
            
            page.update()
            await asyncio.sleep(0.016)

    return ft.View(
        "/pvc",
        bgcolor="black",
        padding=0,
        controls=[
            game_stack,
            ft.TextButton("QUITTER", on_click=lambda _: page.go("/"), style=ft.ButtonStyle(color=NEON_CYAN))
        ]
    )