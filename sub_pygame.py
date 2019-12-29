import sys, os
import pygame
import locale
from pygame.locals import *

colors = {
    "grey_light"    :   pygame.Color(200, 200, 200),
    "grey_dark"     :   pygame.Color(100, 100, 100),
    "green"         :   pygame.Color(50, 255, 63),
    "red"           :   pygame.Color(220, 30, 30),
    "blue"          :   pygame.Color(50, 75, 245)
}


try:
    import pygame.freetype as freetype
except ImportError:
    print ("No FreeType support compiled")
    sys.exit()

def setup():
    pass


def update(milliseconds):  # elapsed time in milliseconds
    pass


def draw(screen):
    pass

def get_font():
    fontdir = os.path.dirname(os.path.abspath(__file__))
    font = freetype.Font(os.path.join(fontdir, "data", "sans.ttf"))

    font.underline_adjustment = 0.5
    font.pad = True

    return font


def print_unicode(s):
    e = locale.getpreferredencoding()
    print (s.encode(e, 'backslashreplace').decode())


def main():
    pygame.init()

    # load and set the logo
    # logo = pygame.image.load("logo32x32.png")
    # pygame.display.set_icon(logo)

    # Screen setup
    pygame.display.set_caption("Sub Simulator")
    print(pygame.display.Info())

    screen = pygame.display.set_mode((640, 480))
    #screen.fill((0, 0, 0))

    clock = pygame.time.Clock()

    font = get_font()

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    running = True
    setup()
    while running:
        milliseconds = clock.tick(500)
        update(milliseconds)
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False


        # print FPS

        s, r = font.render( "{:.0f} fps".format(clock.get_fps()),
                       colors['grey_light'],
                       size=12, style=freetype.STYLE_NORMAL)

        screen.blit(s, (600, 4))

        draw(screen)
        pygame.display.update(r)

    pygame.quit()

        # if pygame.event.wait().type in (QUIT, KEYDOWN, MOUSEBUTTONDOWN):
        #     break


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    # call the main function
    main()