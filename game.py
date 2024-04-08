import json
import pygame
import sys
from typing import List, Dict
import scr.PyPlots as PyPlots

ground: List[PyPlots.solid.Rect] = []
entity: Dict[str, PyPlots.entity.Rect] = {}
triggers: Dict[str, PyPlots.trigger.Rect] = {}
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
        triggers.update({trigger_rects.name: trigger_rects})

player = entity["player"]
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen_ratio = PyPlots.screen.get_width()/1600 
    delta_time = PyPlots.clock.tick()/100

    keys = pygame.key.get_pressed()

    pygame.display.set_caption(f"FPS, {PyPlots.clock.get_fps()}")

    PyPlots.screen.fill((255, 255, 255))

    if keys[pygame.K_UP] and triggers["on ground"].trigger(ground):
        player.velocity.y = 60
        jumping = True
    elif keys[pygame.K_UP] and jumping and player.velocity.y > 0:
        player.velocity.y += 27 * delta_time
    else:
        jumping = False

    if triggers["on ground"].trigger(ground) and player.velocity.y <= 0:
        player.velocity.y = 0
    if not triggers["on ground"].trigger(ground):
        player.velocity.y -= 40 * delta_time
    if player.velocity.y < -150:
        player.velocity.y = -150
    player.move(pygame.Vector2(0, -player.velocity.y * delta_time))
    
    player.move(pygame.Vector2(40 * (
        keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        )* delta_time, 0), ground)
    
    for g in ground:
        pygame.draw.rect(PyPlots.screen, g.color, g.rect())
    pygame.draw.rect(PyPlots.screen, player.color, player.rect())
    pygame.draw.rect(PyPlots.screen, (0,0,0), triggers["on ground"].rect())

    pygame.display.flip()

pygame.quit()
sys.exit()