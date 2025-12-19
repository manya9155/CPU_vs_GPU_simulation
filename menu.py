import pygame

def choose_shape():
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Choose Shape")

    font = pygame.font.SysFont(None, 36)
    options = ["Triangle", "Square", "Rectangle"]
    selected = 0

    running = True
    while running:
        screen.fill((30, 30, 30))
        for i, opt in enumerate(options):
            color = (255,255,0) if i == selected else (200,200,200)
            text = font.render(opt, True, color)
            screen.blit(text, (120, 80 + i*50))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % 3
                if e.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3
                if e.key == pygame.K_RETURN:
                    pygame.quit()
                    return options[selected].lower()
