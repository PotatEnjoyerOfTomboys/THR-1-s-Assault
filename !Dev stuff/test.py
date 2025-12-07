import pygame

pygame.init()

display = pygame.display.set_mode((400, 400))


def draw_circle_arc(dest: pygame.Surface):
    angle_1 = 1  # rad
    angle_2 = 2  # rad
    arc_rect = (10, 10, 100, 100)
    pygame.draw.arc(dest, "red", arc_rect, angle_1, angle_2, 100000)
    # NOTE 1: angles are in RADIANS (for some reason)
    # NOTE 2: for this to work as you want, the 'width' parameter needs to be very big, but, of course, you can set it to whatever you like


while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            quit()

    display.fill("black")
    draw_circle_arc(display)
    pygame.display.update()