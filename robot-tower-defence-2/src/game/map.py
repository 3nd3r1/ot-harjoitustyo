""" src/game/map.py """
import pytmx
import pygame
from utils.config import arenas
from utils.file_reader import get_tmx


class Map:
    """
      This class represents the map on which the game is played.
      It has methods for loading and displaying the map. 
    """

    def __init__(self, arena: str) -> None:

        self.__tmx = pytmx.load_pygame(
            get_tmx(arenas[arena]["map_file"]))

        self.__width = self.__tmx.width * self.__tmx.tilewidth
        self.__height = self.__tmx.height * self.__tmx.tileheight
        self.__map = pygame.Surface((self.__width, self.__height))
        self.__obstacles = []
        self.__water = []

        self.render_map()

    def render_map(self) -> None:
        """ Renders an image of the map """
        tw = self.__tmx.tilewidth
        th = self.__tmx.tileheight
        for layer in self.__tmx.visible_layers:
            for x, y, gid in layer:
                tile = self.__tmx.get_tile_image_by_gid(gid)
                if tile:
                    self.__map.blit(tile, (x*th, y*tw))
                    if layer.name == "obstacles" or layer.name == "obstacles2":
                        self.__obstacles.append(
                            pygame.Rect(x*tw, y*th, tw, th))
                    if layer.name == "water":
                        self.__water.append(pygame.Rect(x*tw, y*th, tw, th))

    def draw(self, surface) -> None:
        """ Draws the image of the map to the main surface """
        surface.blit(self.__map, (188, 105))