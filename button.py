import pygame
from const import *

# https://github.com/Unlim8ted-Studio-Productions/Easy_pygame_UI-Maker/blob/main/button.py

class Button:
    """Button class for creating interactive buttons in the game."""

    def __init__(
        self,
        text,
        x,
        y,
        width,
        height,
        command,
        additional_data: list = None,
        color=WHITE,
    ):
        """
        Initialize a button.

        Args:
            text (str): The text displayed on the button.
            x (int): The x-coordinate of the button's top-left corner.
            y (int): The y-coordinate of the button's top-left corner.
            width (int): The width of the button.
            height (int): The height of the button.
            command (function): The function to be executed when the button is clicked.
            aditional data (list): arguments the buttons command needs to run
        """
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.command = command
        self.additional_data = additional_data
        self.hovered = False
        self.size = 36
        self.active = False
        self.bold = False
        self.italics = False
        self.underlined = False
        self.font_name = "fonts/PixelifySans-Regular.ttf"
        self.color = color

    def draw(self, screen):
        """Draw the button on the screen."""
        font = pygame.font.Font(self.font_name, self.size)
        font.set_bold(self.bold)
        font.set_italic(self.italics)
        font.set_underline(self.underlined)
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        text = font.render(self.text, True, self.color)
        screen.blit(
            text,
            (
                self.x + self.width // 2 - text.get_width() // 2,
                self.y + self.height // 2 - text.get_height() // 2,
            ),
        )

    def handle_event(self, event):
        """
        Handle events related to the button.

        Args:
            event: The Pygame event to be processed.
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = (
                self.x < event.pos[0] < self.x + self.width
                and self.y < event.pos[1] < self.y + self.height
            )
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.active = True
                if self.additional_data != None:
                    self.command(*self.additional_data)
                else:
                    self.command()
            else:
                self.active = False

    def selected(self): 
        self.hovered = True

    def change_text(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = (
                self.x < event.pos[0] < self.x + self.width
                and self.y < event.pos[1] < self.y + self.height
            )
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode