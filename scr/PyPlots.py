import json
from types import UnionType
import pygame
import sys
from typing import List, Dict

pygame.init()
if True :
    screen_size = pygame.display.Info().current_w
    screen = pygame.display.set_mode((screen_size, screen_size/16*9), pygame.FULLSCREEN, display=0)
else:
    screen_size = 600
    screen = pygame.display.set_mode((screen_size, screen_size/16*9), display=0)
screen_ratio = screen_size/1600
print(screen_ratio, screen_size)

clock = pygame.time.Clock()
clock.tick(60)

game_object_id: int = 0
Game_object: Dict = {}

class transform:
    class Rect:
        def __init__(self, left: int = 0, top: int = 0, width: int = 0, height: int = 0):
            self.left: int = left
            self.top: int = top
            self.width: int = width
            self.height: int = height
        
        def getvalues(self) -> tuple:
            return (self.left, self.top, self.width, self.height)

class solid:
    class Rect:
        def __init__(
                self,
                transform_: tuple = (0, 0, 0, 0),
                color: tuple = (0, 0, 0),
            ):
            global game_object_id
            l, t, w, h = transform_
            self.transform: transform.Rect = transform.Rect(l, t, w, h)
            self.color: tuple = color
            game_object_id += 1
            self.id: int = game_object_id
        
        def rect(self):
            return pygame.Rect(
                int(self.transform.left * screen_ratio),
                int(self.transform.top * screen_ratio),
                int(self.transform.width * screen_ratio),
                int(self.transform.height * screen_ratio)
            )
        
        def from_json(self, data: dict):
            self.transform: transform.Rect = transform.Rect(data["transform"]["left"], data["transform"]["top"], data["transform"]["width"], data["transform"]["height"])
            self.color = (data["color"]["r"], data["color"]["g"], data["color"]["b"])
            self.id = data["id"]
        
        def return_json(self):
            return {
                "transform": {
                    "left": self.transform.left,
                    "top": self.transform.top,
                    "width": self.transform.width,
                    "height": self.transform.height
                },
                "color": {
                    "r": self.color[0],
                    "g": self.color[1],
                    "b": self.color[2]
                },
                "id": self.id
            }

class trigger:
    class Rect:
        def __init__(
                self, 
                transform_: tuple = (0, 0, 0, 0),
                name: str = "trigger"
            ):
            global game_object_id
            l, t, w, h = transform_
            self.transform: transform.Rect = transform.Rect(l, t, w, h)
            game_object_id += 1
            self.id:int = game_object_id
            self.name: str = name
        
        def rect(self):
            return pygame.Rect(
                int(self.transform.left * screen_ratio),
                int(self.transform.top * screen_ratio),
                int(self.transform.width * screen_ratio),
                int(self.transform.height * screen_ratio)
            )

        def from_json(self, data: dict):
            self.transform: transform.Rect = transform.Rect(data["transform"]["left"], data["transform"]["top"], data["transform"]["width"], data["transform"]["height"])
            self.id = data["id"]
            self.name = data["name"]
        
        def return_json(self):
            return {
                "transform": {
                    "left": self.transform.left,
                    "top": self.transform.top,
                    "width": self.transform.width,
                    "height": self.transform.height
                },
                "name": self.name,
                "id": self.id
            }
        
        def trigger(self, triggers: 'solid.Rect'):
            collidelist = [g.rect() for g in triggers]
            if self.rect().collideobjects(collidelist):
                return True
            return False

class entity:
    class Rect:
        def __init__(
                self, 
                transform_: tuple = (0, 0, 0, 0),
                color: tuple = (0, 0, 0), 
                velocity: pygame.Vector2 = pygame.Vector2(0, 0),
                name: str = "entity"
            ):
            global game_object_id
            l, t, w, h = transform_
            self.transform: transform.Rect = transform.Rect(l, t, w, h)
            self.color: tuple = color
            self.velocity: pygame.Vector2 = velocity
            self.name: str = name
            game_object_id += 1
            self.id: int = game_object_id
            self.childrenid: List[int] = []
        
        def rect(self):
            return pygame.Rect(
                int(self.transform.left * screen_ratio),
                int(self.transform.top * screen_ratio),
                int(self.transform.width * screen_ratio),
                int(self.transform.height * screen_ratio)
            )
        
        def collideobjectsall(self, collidelist: List):
            returnlist = []
            for c in collidelist:
                if (
                    (self.transform.left < c.transform.left + c.transform.width and 
                     self.transform.left + self.transform.width > c.transform.left) and
                    (self.transform.top < c.transform.top + c.transform.height and 
                     self.transform.top + self.transform.height > c.transform.top)
                ):
                    returnlist.append(c)
            return returnlist
        
        
        
        def move(self, move: pygame.Vector2 = pygame.Vector2(0,0), collidelist: List = []):
            colliding = self.collideobjectsall(collidelist)
            if not colliding:
                self.transform.left += move.x
                self.transform.top += move.y
                if self.childrenid:
                    for c in self.childrenid:
                        Game_object[c].transform.left += move.x
                        Game_object[c].transform.top += move.y
            else:
                self.transform.left += move.x
                self.transform.top += move.y
                if self.childrenid:
                    for c in self.childrenid:
                        Game_object[c].transform.left += move.x
                        Game_object[c].transform.top += move.y

                for c in colliding:
                    difflist = [
                        abs(self.transform.left - c.transform.left - c.transform.width),
                        abs(self.transform.top - c.transform.top - c.transform.height),
                        abs(self.transform.left + self.transform.width - c.transform.left),
                        abs(self.transform.top + self.transform.height - c.transform.top)
                    ]
                    if min(difflist) == difflist[0]:
                        self.transform.left += difflist[0] -(1/screen_ratio)
                        if self.childrenid:
                            for ci in self.childrenid:
                                Game_object[ci].transform.left += difflist[0] -(1/screen_ratio)
                    elif min(difflist) == difflist[1]:
                        self.transform.top += difflist[1] -(1/screen_ratio)
                        if self.childrenid:
                            for ci in self.childrenid:
                                Game_object[ci].transform.top += difflist[1] -(1/screen_ratio)
                    elif min(difflist) == difflist[2]:
                        self.transform.left -= difflist[2] -(1/screen_ratio)
                        if self.childrenid:
                            for ci in self.childrenid:
                                Game_object[ci].transform.left -= difflist[2] -(1/screen_ratio)
                    elif min(difflist) == difflist[3]:
                        self.transform.top -= difflist[3] -(1/screen_ratio)
                        if self.childrenid:
                            for ci in self.childrenid:
                                Game_object[ci].transform.top -= difflist[3] -(1/screen_ratio)
        
        def from_json(self, data: json.dumps):
            self.transform: transform.Rect = transform.Rect(data["transform"]["left"], data["transform"]["top"], data["transform"]["width"], data["transform"]["height"])
            self.velocity = pygame.Vector2(data["velocity"]["x"], data["velocity"]["y"])
            self.color = (data["color"]["r"], data["color"]["g"], data["color"]["b"])
            self.name = data["name"]
            self.id = data["id"]
            self.childrenid = data["children"]

        def return_json(self):
            return {
                "transform": {
                    "left": self.transform.left,
                    "top": self.transform.top,
                    "width": self.transform.width,
                    "height": self.transform.height
                },
                "color": {
                    "r": self.color[0],
                    "g": self.color[1],
                    "b": self.color[2]
                },
                "velocity": {
                    "x": self.velocity.x,
                    "y": self.velocity.y
                },
                "name": self.name,
                "id": self.id,
                "children": self.childrenid
            }
