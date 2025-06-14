import pygame
import os
import random
import sys

# --- Настройки ---
SPIN_DURATION = 3
IMAGE_SIZE = (186, 317)
FONT_SIZE = 36

# --- Инициализация Pygame ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
background_image = pygame.image.load("CynoCard.png").convert()  # замените на свой путь
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))


pygame.display.set_caption("Case Opening")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, FONT_SIZE)

# --- Загрузка изображений и звуков ---
image_folder = "BaffsDebaffs"
image_folder2 = "BaffsDebaffsSmall"
sound_folder = "SoundEffects"

images = []
image_names = []

for file in os.listdir(image_folder2):
    if file.lower().endswith((".png", ".jpg")):
        name = os.path.splitext(file)[0]
        img = pygame.image.load(os.path.join(image_folder2, file)).convert_alpha()
        images.append((name, img))
        image_names.append(name)

# Звук "тик"
tick_sound = pygame.mixer.Sound(os.path.join(sound_folder, "tick.wav"))

reward_sounds = {}
for name in image_names:
    path = os.path.join(sound_folder, f"{name}.wav")
    if os.path.exists(path):
        reward_sounds[name] = pygame.mixer.Sound(path)

# Удлиняем ленту
image_strip = images * 15

x_positions = [i * (IMAGE_SIZE[0] + 15) for i in range(len(image_strip))]


def draw_button(text, center):
    button_rect = pygame.Rect(0, 0, 300, 60)
    button_rect.center = center
    pygame.draw.rect(screen, (70, 70, 70), button_rect, border_radius=12)
    pygame.draw.rect(screen, (200, 200, 200), button_rect, 2, border_radius=12)

    font = pygame.font.SysFont('hywenhei85w', 25)
    txt = font.render(text, True, (255, 255, 255))
    screen.blit(txt, (button_rect.centerx - txt.get_width() // 2, button_rect.centery - txt.get_height() // 2))
    return button_rect

def draw_close_button():
    size = 40
    padding = 10
    rect = pygame.Rect(SCREEN_WIDTH - size - padding, padding, size, size)

    # Красный квадрат
    pygame.draw.rect(screen, (200, 0, 0), rect, border_radius=5)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=5)

    # Белый крестик
    cx, cy = rect.center
    offset = 10
    pygame.draw.line(screen, (255, 255, 255), (cx - offset, cy - offset), (cx + offset, cy + offset), 3)
    pygame.draw.line(screen, (255, 255, 255), (cx - offset, cy + offset), (cx + offset, cy - offset), 3)

    return rect

def spin_reel():
    random.shuffle(image_strip)
    offset = 0
    speed = random.uniform(30, 100)
    DECELERATION = random.uniform(0.98, 0.999)
    last_tick_index = -1
    running = True
    selected_image = None

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(background_image, (0, 0))

        offset += speed
        speed *= DECELERATION

        # Отрисовка ленты
        for i, (name, img) in enumerate(image_strip):
            x = x_positions[i] - offset
            if -IMAGE_SIZE[0] < x < SCREEN_WIDTH + IMAGE_SIZE[0]:
                screen.blit(img, (x, SCREEN_HEIGHT // 2 - IMAGE_SIZE[1] // 2))

        # Стрелка
        arrow_x = SCREEN_WIDTH // 2
        pygame.draw.polygon(screen, (255, 0, 0), [
            (arrow_x, 350),
            (arrow_x - 25, 190),
            (arrow_x + 25, 190)
        ])

        pygame.display.flip()

        # Определяем пересечение с границей между изображениями
        for i in range(len(x_positions) - 1):
            left_edge = x_positions[i] - offset

            if abs(left_edge - arrow_x) < 2:  # стрелка почти на границе
                if i != last_tick_index:
                    tick_sound.play()
                    last_tick_index = i
                    selected_image = image_strip[i]
                break

        if abs(speed) < 0.1:
            running = False

    return selected_image

def show_winner(image_tuple):
    name1, _ = image_tuple

    original_path = os.path.join(image_folder, f"{name1}.png")
    if not os.path.exists(original_path):
        original_path = os.path.join(image_folder, f"{name1}.jpg")

    full_img = pygame.image.load(original_path).convert_alpha()

    screen.blit(background_image, (0, 0))
    screen.blit(full_img, ((SCREEN_WIDTH - full_img.get_width()) // 2, (SCREEN_HEIGHT - full_img.get_height()) // 2))
    pygame.display.flip()

    # Проигрываем звук выигрыша
    if name1 in reward_sounds:
        reward_sounds[name1].play()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                waiting = False

# --- Главный цикл ---
def main():
    while True:
        screen.blit(background_image, (0, 0))
        btn_rect = draw_button("Помолиться", (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        close_btn_rect = draw_close_button()
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_rect.collidepoint(event.pos):
                        waiting = False
                    elif close_btn_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
        winner = spin_reel()
        pygame.time.wait(300)
        if winner:
            show_winner(winner)


if __name__ == "__main__":
    main()

