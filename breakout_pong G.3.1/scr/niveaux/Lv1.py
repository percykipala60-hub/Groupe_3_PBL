import flet as ft
import random
import asyncio

WIDTH = 400
HEIGHT = 700
PADDLE_WIDTH = 120
PADDLE_HEIGHT = 12
BALL_SIZE = 12
SPEED = 8  # Vitesse de la balle augmentée
ROWS = 5
COLS = 6
BRICK_WIDTH = WIDTH / COLS
BRICK_HEIGHT = 25

# 🎨 Couleurs Néon
NEON_CYAN = "#00D9FF"
NEON_MAGENTA = "#FF00FF"
NEON_PINK = "#FF006E"
NEON_GREEN = "#39FF14"
NEON_PURPLE = "#B700FF"

def get_lv1_view(page: ft.Page):
    ball_x = WIDTH / 2
    ball_y = HEIGHT - 60
    dx, dy = 0, 0
    paddle_x = WIDTH / 2 - PADDLE_WIDTH / 2
    ball_launched = False
    launch_timer = 90  # 1.5 secondes avant lancer automatique
    keys_pressed = {}
    score = 0
    lives = 3

    # 🎾 Balle néon
    ball = ft.Container(
        width=BALL_SIZE, height=BALL_SIZE, 
        bgcolor=NEON_CYAN,
        border_radius=6, 
        left=ball_x, top=ball_y,
        shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN)
    )
    
    # 🏓 Pagaie néon
    paddle = ft.Container(
        width=PADDLE_WIDTH, height=PADDLE_HEIGHT, 
        bgcolor=NEON_MAGENTA,
        left=paddle_x, top=HEIGHT - 40,
        shadow=ft.BoxShadow(blur_radius=15, color=NEON_MAGENTA)
    )
    
    bricks = []
    bricks_stack = ft.Stack()

    def build_bricks():
        bricks.clear()
        bricks_stack.controls.clear()
        colors = [NEON_PINK, NEON_GREEN, NEON_CYAN, NEON_PURPLE, NEON_MAGENTA]
        for row in range(ROWS):
            for col in range(COLS):
                color = colors[row % len(colors)]
                brick = ft.Container(
                    width=BRICK_WIDTH - 5, height=BRICK_HEIGHT - 5,
                    bgcolor=color, 
                    left=col * BRICK_WIDTH + 2, 
                    top=row * BRICK_HEIGHT + 40,
                    shadow=ft.BoxShadow(blur_radius=8, color=color)
                )
                bricks.append(brick)
                bricks_stack.controls.append(brick)

    build_bricks()
    
    # 📊 Score et Vies
    score_text = ft.Text(value="Score: 0", color=NEON_GREEN, size=20, left=10, top=10, weight="bold")
    lives_text = ft.Text(value="❤️ ❤️ ❤️", color=NEON_PINK, size=20, left=WIDTH - 100, top=10, weight="bold")

    def restart_game(e):
        nonlocal lives, score, ball_launched, ball_x, ball_y, dx, dy, paddle_x, launch_timer
        lives, score = 3, 0
        ball_launched = False
        launch_timer = 90
        ball_x = WIDTH / 2
        ball_y = HEIGHT - 60
        dx, dy = 0, 0
        paddle_x = WIDTH / 2 - PADDLE_WIDTH / 2
        paddle.left = paddle_x
        score_text.value = "Score: 0"
        lives_text.value = "❤️ ❤️ ❤️"
        game_over_screen.visible = False
        victory_screen.visible = False
        build_bricks()
        page.update()

    # 💀 Écran Game Over
    game_over_screen = ft.Container(
        content=ft.Column([
            ft.Text("GAME OVER", color=NEON_PINK, size=60, weight="bold", italic=True, text_align=ft.TextAlign.CENTER),
            ft.Text(f"Score: {score}", color=NEON_GREEN, size=30, weight="bold", text_align=ft.TextAlign.CENTER),
            ft.ElevatedButton(
                "Recommencer", 
                on_click=restart_game, 
                width=200,
                style=ft.ButtonStyle(bgcolor={"": NEON_MAGENTA}, color={"": "white"})
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
        width=WIDTH, height=HEIGHT, 
        bgcolor=ft.Colors.with_opacity(0.9, "black"), 
        visible=False, left=0, top=0
    )

    # 🏆 Écran Victoire
    victory_screen = ft.Container(
        content=ft.Column([
            ft.Text("VICTOIRE !", color=NEON_CYAN, size=60, weight="bold", italic=True, text_align=ft.TextAlign.CENTER),
            ft.Text(f"Score: {score}", color=NEON_GREEN, size=30, weight="bold", text_align=ft.TextAlign.CENTER),
            ft.ElevatedButton(
                "Rejouer", 
                on_click=restart_game, 
                width=200,
                style=ft.ButtonStyle(bgcolor={"": NEON_CYAN}, color={"": "black"})
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
        width=WIDTH, height=HEIGHT, 
        bgcolor=ft.Colors.with_opacity(0.9, "black"), 
        visible=False, left=0, top=0
    )

    # 🎮 Stack du jeu
    game_stack = ft.Stack(
        width=WIDTH, height=HEIGHT,
        controls=[
            ft.Container(width=WIDTH, height=2, bgcolor=NEON_CYAN, top=0, shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN)),
            ft.Container(width=WIDTH, height=2, bgcolor=NEON_CYAN, top=HEIGHT - 2, shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN)),
            ft.Container(width=2, height=HEIGHT, bgcolor=NEON_CYAN, left=0, shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN)),
            ft.Container(width=2, height=HEIGHT, bgcolor=NEON_CYAN, left=WIDTH - 2, shadow=ft.BoxShadow(blur_radius=10, color=NEON_CYAN)),
            bricks_stack, ball, paddle, score_text, lives_text, game_over_screen, victory_screen
        ]
    )

    def update_game():
        nonlocal ball_x, ball_y, dx, dy, paddle_x, score, lives, ball_launched, launch_timer
        if game_over_screen.visible or victory_screen.visible: return

        # Paddle (clampé)
        if is_key_pressed(VK_LEFT): paddle_x = max(0, paddle_x - 10)
        if is_key_pressed(VK_RIGHT): paddle_x = min(WIDTH - PADDLE_WIDTH, paddle_x + 10)
        paddle.left = paddle_x

        if (is_key_pressed(VK_SPACE) or is_key_pressed(VK_RETURN)) and not ball_launched:
            launch(None)

        if not ball_launched:
            ball_x = paddle_x + PADDLE_WIDTH / 2 - BALL_SIZE / 2
            ball_y = HEIGHT - 65
            if launch_timer > 0:
                launch_timer -= 1
            else:
                launch(None)
        else:
            ball_x += dx
            ball_y += dy

            # Rebond murs latéraux (clampage strict)
            if ball_x <= 0:
                ball_x = 1
                dx = abs(dx)
            elif ball_x >= WIDTH - BALL_SIZE:
                ball_x = WIDTH - BALL_SIZE - 1
                dx = -abs(dx)

            # Rebond mur du haut
            if ball_y <= 0:
                ball_y = 1
                dy = abs(dy)

            # Collision raquette (anti-stuck)
            if (dy > 0 and paddle.left <= ball_x + BALL_SIZE/2 <= paddle.left + PADDLE_WIDTH
                    and ball_y + BALL_SIZE >= paddle.top):
                # Calcul de l'angle basé sur le point d'impact
                paddle_center = paddle.left + PADDLE_WIDTH / 2
                ball_center = ball_x + BALL_SIZE / 2
                relative_intersect_x = ball_center - paddle_center
                normalized_intersect_x = relative_intersect_x / (PADDLE_WIDTH / 2)
                
                dx = normalized_intersect_x * (SPEED * 1.5)
                dy = -abs(dy)
                ball_y = paddle.top - BALL_SIZE

            # Collision briques
            for brick in bricks[:]:
                if (brick.left <= ball_x <= brick.left + BRICK_WIDTH and brick.top <= ball_y <= brick.top + BRICK_HEIGHT):
                    bricks.remove(brick)
                    bricks_stack.controls.remove(brick)
                    dy *= -1
                    score += 1
                    score_text.value = f"Score: {score}"
                    if len(bricks) == 0:
                        victory_screen.visible = True
                        ball_launched = False
                    break

        if ball_y >= HEIGHT:
            lives -= 1
            lives_text.value = "❤️" * lives
            if lives <= 0:
                game_over_screen.visible = True
            else:
                ball_launched = False
                launch_timer = 90

        ball.left, ball.top = ball_x, ball_y

    async def game_loop():
        while page.route == "/lv1":
            update_game()
            page.update()
            await asyncio.sleep(0.016)

    def launch(e):
        nonlocal ball_launched, dx, dy
        if not ball_launched:
            ball_launched = True
            dx, dy = random.choice([-6.5, 6.5]), -SPEED

    # --- Événements clavier natifs ultra-rapides (Windows) ---
    import ctypes
    def is_key_pressed(vk):
        return (ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000) != 0
    VK_LEFT, VK_RIGHT, VK_SPACE, VK_RETURN = 0x25, 0x27, 0x20, 0x0D

    def move_paddle(e: ft.DragUpdateEvent):
        nonlocal paddle_x
        if not game_over_screen.visible and not victory_screen.visible:
            paddle_x = max(0, min(WIDTH - PADDLE_WIDTH, paddle_x + e.delta_x))
            paddle.left = paddle_x
            page.update()

    paddle.on_click = launch
    paddle.on_pan_update = move_paddle
    page.run_task(game_loop)

    # --- Contrôles tactiles (Boutons flèches) ---
    def on_btn_down(key):
        keys_pressed[key] = True

    def on_btn_up(key):
        keys_pressed[key] = False

    touch_controls = ft.Row(
        [
            ft.GestureDetector(
                content=ft.Container(
                    content=ft.Icon(ft.Icons.ARROW_LEFT, color=NEON_CYAN, size=50),
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.1, NEON_CYAN),
                    border_radius=10,
                ),
                on_tap_down=lambda _: on_btn_down("ArrowLeft"),
                on_tap_up=lambda _: on_btn_up("ArrowLeft"),
            ),
            ft.Container(width=50),
            ft.GestureDetector(
                content=ft.Container(
                    content=ft.Icon(ft.Icons.ARROW_RIGHT, color=NEON_CYAN, size=50),
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.1, NEON_CYAN),
                    border_radius=10,
                ),
                on_tap_down=lambda _: on_btn_down("ArrowRight"),
                on_tap_up=lambda _: on_btn_up("ArrowRight"),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return ft.View(
        "/lv1",
        bgcolor="black",
        padding=0,
        controls=[
            game_stack, 
            ft.TextButton(
                "← RETOUR", 
                on_click=lambda _: page.go("/niveaux"), 
                style=ft.ButtonStyle(color=NEON_CYAN)
            )
        ]
    )