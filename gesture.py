import cv2
import mediapipe as mp
import pygame
import random

# -------------------- MediaPipe Setup --------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# -------------------- Pygame Setup --------------------
pygame.init()

WIDTH, HEIGHT = 600, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Snake Game")

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

clock = pygame.time.Clock()
block = 20
speed = 10

# -------------------- Snake Setup --------------------
snake = [(300, 300)]
direction = "RIGHT"

food = (random.randrange(0, WIDTH, block),
        random.randrange(0, HEIGHT, block))

# -------------------- Webcam --------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not working")
    exit()

def get_hand_direction(frame, current_direction):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    new_direction = current_direction

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            index_tip = handLms.landmark[8]
            cx, cy = int(index_tip.x * w), int(index_tip.y * h)

            center_x = w // 2
            center_y = h // 2

            if abs(cx - center_x) > abs(cy - center_y):
                new_direction = "LEFT" if cx < center_x else "RIGHT"
            else:
                new_direction = "UP" if cy < center_y else "DOWN"

    return new_direction, frame

# -------------------- Game Loop --------------------
running = True

while running:
    clock.tick(speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Webcam Frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.flip(frame, 1)

    direction, frame = get_hand_direction(frame, direction)

    # Move Snake
    head_x, head_y = snake[0]

    if direction == "UP":
        head_y -= block
    elif direction == "DOWN":
        head_y += block
    elif direction == "LEFT":
        head_x -= block
    elif direction == "RIGHT":
        head_x += block

    new_head = (head_x, head_y)
    snake.insert(0, new_head)

    # Food Collision
    if new_head == food:
        food = (random.randrange(0, WIDTH, block),
                random.randrange(0, HEIGHT, block))
    else:
        snake.pop()

    # Wall or Self Collision
    if (head_x < 0 or head_x >= WIDTH or
        head_y < 0 or head_y >= HEIGHT or
        new_head in snake[1:]):
        print("Game Over")
        running = False

    # Draw Game
    win.fill(WHITE)

    for segment in snake:
        pygame.draw.rect(win, GREEN,
                         (segment[0], segment[1], block, block))

    pygame.draw.rect(win, RED,
                     (food[0], food[1], block, block))

    pygame.display.flip()

    # Show camera window
    cv2.imshow("Hand Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        running = False

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()