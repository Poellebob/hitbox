import json
import pygame
import sys
from typing import List, Dict

pygame.init()
screen_size = pygame.display.Info().current_w
screen = pygame.display.set_mode((screen_size, screen_size/16*9), pygame.FULLSCREEN, display=0)
screen_ratio = screen_size/1600

clock = pygame.time.Clock()
clock.tick(60)

game_object_id: int = 0
Game_object: Dict = {}
class game_object:
    class transform:
        class Rect:
            def __init__(self, left: int = 0, top: int = 0, width: int = 0, height: int = 0):
                self.left: int = left
                self.top: int = top
                self.width: int = width
                self.height: int = height
            
            def getvalues(self):
                return self.left, self.top, self.width, self.height

    class solid:
        class Rect:
            def __init__(
                    self,
                    transform: tuple = (0, 0, 0, 0),
                    color: tuple = (0, 0, 0),
                ):
                global game_object_id
                l, t, w, h = transform
                self.transform: game_object.transform.Rect = game_object.transform.Rect(l, t, w, h)
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
                self.transform: game_object.transform.Rect = game_object.transform.Rect(data["transform"]["left"], data["transform"]["top"], data["transform"]["width"], data["transform"]["height"])
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
                    transform: tuple = (0, 0, 0, 0),
                    name: str = "trigger"
                ):
                global game_object_id
                l, t, w, h = transform
                self.transform: game_object.transform.Rect = game_object.transform.Rect(l, t, w, h)
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
                self.transform: game_object.transform.Rect = game_object.transform.Rect(data["transform"]["left"], data["transform"]["top"], data["transform"]["width"], data["transform"]["height"])
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
            
            def trigger(self, triggers: 'game_object.solid.Rect'):
                collidelist = [g.rect() for g in triggers]
                if self.rect().collideobjects(collidelist):
                    return True
                return False

    class entity:
        class Rect:
            def __init__(
                    self, 
                    transform: tuple = (0, 0, 0, 0),
                    color: tuple = (0, 0, 0), 
                    velocity: pygame.Vector2 = pygame.Vector2(0, 0),
                    name: str = "entity"
                ):
                global game_object_id
                l, t, w, h = transform
                self.transform: game_object.transform.Rect = game_object.transform.Rect(l, t, w, h)
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
            
            def move(self, move: pygame.Vector2 = pygame.Vector2(0,0), collidelist: List['game_object.solid.Rect'] = []):
                obl = []
                if collidelist:
                    for c in collidelist:
                        obl.append(c.rect())
                colliding: List[pygame.Rect] = self.rect().collideobjectsall(obl)
                
                self.transform.left += move.x
                self.transform.top += move.y
                if self.childrenid:
                    for c in self.childrenid:
                        Game_object[c].transform.left += move.x
                        Game_object[c].transform.top += move.y
                
                if colliding:
                    for c in colliding:
                        c = pygame.Rect(c)
                        points: List[pygame.Rect] = [
                            abs(c.top - self.rect().bottom), 
                            abs(c.bottom - self.rect().top), 
                            abs(c.left - self.rect().right), 
                            abs(c.right - self.rect().left)
                        ]
                        points_index: int = points.index(min(points))
                        if points_index == 0:
                            self.move(pygame.Vector2(0, -points[points_index]))
                        elif points_index == 1:
                            self.move(pygame.Vector2(0, points[points_index]))
                        elif points_index == 2:
                            self.move(pygame.Vector2(-points[points_index], 0))
                        elif points_index == 3:
                            self.move(pygame.Vector2(points[points_index], 0))
            
            def from_json(self, data: json.dumps):
                self.transform: game_object.transform.Rect = game_object.transform.Rect(data["transform"]["left"], data["transform"]["top"], data["transform"]["width"], data["transform"]["height"])
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

ground: List[game_object.solid.Rect] = []
entity: Dict[str, game_object.entity.Rect] = {}
trigger: Dict[str, game_object.trigger.Rect] = {}
with open("player.json", "r") as file:
    load_data = json.load(file)
    
    entity_load = load_data["game_object"]["entity"]
    for e in entity_load:
        entity_rects = game_object.entity.Rect()
        entity_rects.from_json(e)
        Game_object.update({entity_rects.id: entity_rects})
        entity.update({entity_rects.name: entity_rects})

    ground_load = load_data["game_object"]["ground"]
    for g in ground_load:
        ground_rects = game_object.solid.Rect()
        ground_rects.from_json(g)
        Game_object.update({ground_rects.id: ground_rects})
        ground.append(ground_rects)
    
    trigger_load = load_data["game_object"]["trigger"]
    for t in trigger_load:
        trigger_rects = game_object.trigger.Rect()
        trigger_rects.from_json(t)
        Game_object.update({trigger_rects.id: trigger_rects})
        trigger.update({trigger_rects.name: trigger_rects})

selected = None
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen_ratio = screen.get_width()/1600
    delta_time = clock.tick()/100

    screen.fill((255, 255, 255))

    mouse = (pygame.mouse.get_pos()[0]/screen_ratio, pygame.mouse.get_pos()[1]/screen_ratio)
    click = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    hover: List = []

    for o in Game_object.values():
        if o.transform.left <= mouse[0] and o.transform.left + o.transform.width >= mouse[0] and o.transform.top <= mouse[1] and o.transform.top + o.transform.height >= mouse[1]:
            hover.append(o)
    
    if click[0]:
        for o in hover:
            if click[0]:
                selected = o
                break
        
    if selected:
        if keys[pygame.K_LEFT]:
            selected.transform.left -= 1
        if keys[pygame.K_RIGHT]:
            selected.transform.left += 1
        if keys[pygame.K_UP]:
            selected.transform.top -= 1
        if keys[pygame.K_DOWN]:
            selected.transform.top += 1
    
    for g in ground:
        pygame.draw.rect(screen, (0, 255, 0), g.rect())
    for e in entity.values():
        pygame.draw.rect(screen, e.color, e.rect())
    for t in trigger.values():
        pygame.draw.rect(screen, (0, 0, 0), t.rect())

    pygame.display.flip()

ground_load = [load.return_json() for load in ground]
trigger_load = [load.return_json() for load in trigger.values()]
entity_load = [load.return_json() for load in entity.values()]
load_data = {      
    "game_object": {
        "entity": entity_load,
        "ground": ground_load,
        "trigger": trigger_load
    }
}

with open("player.json", "w") as file:
    json.dump(load_data, file)

pygame.quit()
sys.exit()