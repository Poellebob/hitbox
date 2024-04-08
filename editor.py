import json
import pygame
import sys
from typing import List, Dict
import scr.PyPlots as PyPlots

ground: List[PyPlots.solid.Rect] = []
entity: Dict[str, PyPlots.entity.Rect] = {}
trigger: Dict[str, PyPlots.trigger.Rect] = {}
with open("player.json", "r") as file:
    load_data = json.load(file)
    
    entity_load = load_data["gameobject"]["entity"]
    for e in entity_load:
        entity_rects = PyPlots.entity.Rect()
        entity_rects.from_json(e)
        PyPlots.Game_object.update({entity_rects.id: entity_rects})
        entity.update({entity_rects.name: entity_rects})

    ground_load = load_data["gameobject"]["ground"]
    for g in ground_load:
        ground_rects = PyPlots.solid.Rect()
        ground_rects.from_json(g)
        PyPlots.Game_object.update({ground_rects.id: ground_rects})
        ground.append(ground_rects)
    
    trigger_load = load_data["gameobject"]["trigger"]
    for t in trigger_load:
        trigger_rects = PyPlots.trigger.Rect()
        trigger_rects.from_json(t)
        PyPlots.Game_object.update({trigger_rects.id: trigger_rects})
        trigger.update({trigger_rects.name: trigger_rects})

presseing = False
currentaction = None
mouseposold = (0, 0)
selected = None
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen_ratio = PyPlots.screen.get_width()/1600
    delta_time = PyPlots.clock.tick()/100

    PyPlots.screen.fill((255, 255, 255))

    mouse = (pygame.mouse.get_pos()[0]/screen_ratio, pygame.mouse.get_pos()[1]/screen_ratio)
    click = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    hover: List = []

    for o in PyPlots.Game_object.values():
        if o.transform.left <= mouse[0] and o.transform.left + o.transform.width >= mouse[0] and o.transform.top <= mouse[1] and o.transform.top + o.transform.height >= mouse[1]:
            hover.append(o)
    
    if click[0]:
        for o in hover:
            selected = o
            break
        
    mousevector = (mouse[0] - mouseposold[0], mouse[1] - mouseposold[1])
    mouseposold = mouse
    if not presseing:
        if keys[pygame.K_g] and currentaction != pygame.K_g:
            currentaction = pygame.K_g
            presseing = True
    if currentaction:
        if (keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER] or keys[currentaction] or click[0]) and not presseing:
            currentaction = None
            selected = None
            presseing = True
    
    if presseing and currentaction:
        if not keys[currentaction]:
            presseing = False
    elif not currentaction:
        presseing = False
    if not selected:
        currentaction = None

    if selected:
        if currentaction == pygame.K_g:
            selected.transform.left += mousevector[0] 
            selected.transform.top += mousevector[1] 
    
    for g in ground:
        pygame.draw.rect(PyPlots.screen, (0, 255, 0), g.rect())
    for e in entity.values():
        pygame.draw.rect(PyPlots.screen, e.color, e.rect())
    for t in trigger.values():
        pygame.draw.rect(PyPlots.screen, (0, 0, 0), t.rect())

    pygame.display.flip()

ground_load = [load.return_json() for load in ground]
trigger_load = [load.return_json() for load in trigger.values()]
entity_load = [load.return_json() for load in entity.values()]
load_data = {      
    "gameobject": {
        "entity": entity_load,
        "ground": ground_load,
        "trigger": trigger_load
    }
}

with open("player.json", "w") as file:
    json.dump(load_data, file)

pygame.quit()
sys.exit()