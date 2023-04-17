""" src/game/towers/missile_launcher.py """
import pygame

from game.tower import Tower
from game.projectile import Projectile

from utils.config import towers
from utils.file_reader import get_image


class MissileLauncher(Tower):
    """ Missile Launcher tower class """

    images = {}

    def __init__(self, game) -> None:
        self.__can_be_in_water = towers["missile_launcher"]["can_be_in_water"]
        self.__range = towers["missile_launcher"]["range"]
        self.__shoot_interval = towers["missile_launcher"]["shoot_interval"]
        self.__cost = towers["missile_launcher"]["cost"]
        self.__hitbox = pygame.Rect(0, 0, 60, 60)

        super().__init__(game)

    @staticmethod
    def load_images() -> None:
        base = pygame.image.load(get_image(towers["base"]))
        model_1 = pygame.image.load(get_image(towers["missile_launcher"]["model_1"]))
        model_2 = pygame.image.load(get_image(towers["missile_launcher"]["model_2"]))
        model_3 = pygame.image.load(get_image(towers["missile_launcher"]["model_3"]))

        base = pygame.transform.scale_by(base, 0.25)
        model_1 = pygame.transform.scale_by(model_1, 0.35)
        model_2 = pygame.transform.scale_by(model_2, 0.35)
        model_3 = pygame.transform.scale_by(model_3, 0.35)

        MissileLauncher.images["base"] = base
        MissileLauncher.images["model_1"] = model_1
        MissileLauncher.images["model_2"] = model_2
        MissileLauncher.images["model_3"] = model_3

        MissileLauncherProjectile.load_images()

    @staticmethod
    def render_tower(angle: float) -> pygame.Surface:
        """ Renders the tower """
        screen = pygame.Surface((150, 150), pygame.constants.SRCALPHA, 32)
        base = MissileLauncher.images["base"]
        model_1 = MissileLauncher.images["model_1"]

        tower_offset = pygame.math.Vector2(0, -15)

        model_1 = pygame.transform.rotate(model_1, -angle)
        tower_offset = tower_offset.rotate(angle)

        base_rect = base.get_rect(center=screen.get_rect().center)
        tower_rect = model_1.get_rect(
            center=base_rect.center).move(tower_offset)

        screen.blit(base, base_rect)
        screen.blit(model_1, tower_rect)
        return screen

    def _draw_tower(self):
        """ Draws the tower to the sprite image """
        target_angle = self.get_target_angle()

        self.image = MissileLauncher.render_tower(target_angle)

        time_now = pygame.time.get_ticks()
        if time_now-self.get_last_shot() >= self.get_shoot_interval():
            projectile_image = MissileLauncherProjectile.render_projectile(target_angle)
            projectile_rect = projectile_image.get_rect(
                center=(self.rect.width//2, self.rect.height//2-25))
            self.image.blit(projectile_image, projectile_rect)

    def _shoot(self):
        """ Shoots a turret projectile """
        if not self.get_target():
            return
        self.get_game().add_projectile(
            MissileLauncherProjectile(self.get_target(), self.rect.center))

    def can_be_in_water(self) -> bool:
        """ Returns if the tower can be in water """
        return self.__can_be_in_water

    def get_range(self) -> int:
        """ Returns the range of the tower """
        return self.__range

    def get_shoot_interval(self) -> int:
        return self.__shoot_interval

    def get_hitbox(self):
        self.__hitbox.center = self.rect.center
        return self.__hitbox

    def get_cost(self) -> int:
        return self.__cost


class MissileLauncherProjectile(Projectile):
    images = {}

    def __init__(self, target, starting_pos) -> None:
        self.__speed = towers["missile_launcher"]["projectile_speed"]
        self.__damage = towers["missile_launcher"]["projectile_damage"]

        start_offset = towers["missile_launcher"]["projectile_start_offset"]

        super().__init__(target, starting_pos, start_offset)

    @staticmethod
    def load_images():
        projectile = pygame.image.load(
            get_image(towers["missile_launcher"]["projectile"]))
        projectile = pygame.transform.scale_by(projectile, 0.50)
        MissileLauncherProjectile.images["projectile"] = projectile

    @staticmethod
    def render_projectile(angle):
        """ Renders the projectile """
        screen = pygame.Surface((50, 50), pygame.constants.SRCALPHA, 32)

        projectile = MissileLauncherProjectile.images["projectile"]
        projectile = pygame.transform.rotate(projectile, -angle)

        projectile_rect = projectile.get_rect(
            center=screen.get_rect().center)

        screen.blit(projectile, projectile_rect)
        return screen

    def _draw_projectile(self):
        self.image = MissileLauncherProjectile.render_projectile(
            self.get_target_angle())

    def get_speed(self) -> float:
        return self.__speed

    def get_damage(self) -> int:
        return self.__damage