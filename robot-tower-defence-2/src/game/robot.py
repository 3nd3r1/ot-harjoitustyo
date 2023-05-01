from abc import ABC, abstractmethod
import dataclasses
import pygame

from utils.logger import logger
from utils.config import images
from utils.sheet_reader import get_sheet_images
from utils.math import get_angle


class RobotGroup(pygame.sprite.Group):
    """ A group of robots. """

    def draw(self, screen):
        for robot in self.sprites():
            robot.draw(screen)


@dataclasses.dataclass
class Waypoints:
    waypoints: iter
    current: pygame.math.Vector2

    def next(self):
        self.current = next(self.waypoints, None)


class Robot(pygame.sprite.Sprite, ABC):
    """
    This class represents a robot that moves along the map.
    It has properties such as speed, health, and type,
    and methods for moving and being damaged.
    """

    images = {}

    def __init__(self, game, health: int) -> None:
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.rect = self.image.get_rect()

        self.__velocity = (0, 0)
        self.__health = health

        self.__game = game

        self.__waypoints = Waypoints(iter(self.__get_waypoints()), None)
        self.__waypoints.next()

        self.__last_animation = 0
        self.__animation_frame = 0

        self.rect.center = self.__waypoints.current

        logger.debug(f"Robot ({id(self)}) created with {self.health} HP")

    def __get_waypoints(self) -> list:
        waypoints = self.__game.map.waypoints
        offset_waypoints = []

        for i, waypoint in enumerate(waypoints[:-1]):
            difference_x = waypoints[i+1][0] - waypoint[0]
            difference_y = waypoints[i+1][1] - waypoint[1]

            path_offset = self._path_offset.rotate(get_angle(difference_x, difference_y))
            offset_waypoints.append((round(waypoint[0]+path_offset[0]),
                                    round(waypoint[1]+path_offset[1])))
        offset_waypoints.append(waypoints[-1])

        return offset_waypoints

    @staticmethod
    def load_assets():
        minx_sheet = images["robots"]["minx"]["walk_sheet"]
        minx_sheet_size = images["robots"]["minx"]["walk_sheet_size"]
        nathan_sheet = images["robots"]["nathan"]["walk_sheet"]
        nathan_sheet_size = images["robots"]["nathan"]["walk_sheet_size"]
        archie_sheet = images["robots"]["archie"]["walk_sheet"]
        archie_sheet_size = images["robots"]["archie"]["walk_sheet_size"]

        Robot.images["minx"] = get_sheet_images(minx_sheet, minx_sheet_size)
        Robot.images["nathan"] = get_sheet_images(nathan_sheet, nathan_sheet_size)
        Robot.images["archie"] = get_sheet_images(archie_sheet, archie_sheet_size)

    @staticmethod
    def render(robot_type: str, frame: int) -> pygame.Surface:
        if robot_type == "minx":
            return Robot.images["minx"][frame].copy()
        if robot_type == "nathan":
            return Robot.images["nathan"][frame].copy()
        if robot_type == "archie":
            return Robot.images["archie"][frame].copy()
        return None

    def update(self) -> None:
        if self.health <= 0:
            self.__game.player.earn_money(self.bounty)
            logger.debug(f"Robot ({id(self)}) died")
            self.kill()
            return

        if not self.__waypoints.current:
            self.__game.player.lose_health(self.damage)
            logger.debug(f"Robot ({id(self)}) reached the end of the map")
            self.kill()
            return

        self.__calculate_velocity()
        self.rect.move_ip(self.__velocity)

        if self.__velocity == (0, 0):
            self.__waypoints.next()

    def __calculate_velocity(self):
        waypoint_x = self.__waypoints.current[0]
        waypoint_y = self.__waypoints.current[1]

        velocity_x = min(max(waypoint_x-self.rect.move(self.rect.width//2 +
                         self._path_offset[0], 0).left, -self.speed), self.speed)
        velocity_y = min(max(waypoint_y-self.rect.move(0, self.rect.height +
                         self._path_offset[1]).top, -self.speed), self.speed)

        self.__velocity = (velocity_x, velocity_y)

    def draw(self, screen):
        velocity = self.__velocity
        sheet_width = self._sheet_size[0]
        animation_interval = self._animation_interval
        time_now = pygame.time.get_ticks()

        offset = 0

        if velocity[0] < 0 and velocity[1] == 0:
            offset = sheet_width * 1
        elif velocity[0] > 0 and velocity[1] == 0:
            offset = sheet_width * 3
        elif velocity[0] == 0 and velocity[1] < 0:
            offset = sheet_width * 0
        else:
            offset = sheet_width * 2

        if time_now - self.__last_animation >= animation_interval:
            self.__animation_frame = ((
                self.__animation_frame + 1) % (sheet_width-1))
            self.__last_animation = time_now

        frame = self.__animation_frame + offset

        self.image = Robot.render(self.type, frame)
        screen.blit(self.image, self.rect)

    @property
    def health(self) -> int:
        """This method returns the robot's health."""
        return self.__health

    def lose_health(self, amount: int) -> None:
        """This method decreases the robot's health by the given amount."""
        self.__health = self.__health - amount

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @property
    @abstractmethod
    def damage(self) -> int:
        pass

    @property
    @abstractmethod
    def bounty(self) -> int:
        pass

    @property
    @abstractmethod
    def speed(self) -> int:
        pass

    @property
    @abstractmethod
    def _animation_interval(self) -> int:
        pass

    @property
    @abstractmethod
    def _sheet_size(self) -> tuple:
        pass

    @property
    @abstractmethod
    def _path_offset(self) -> pygame.math.Vector2:
        pass
