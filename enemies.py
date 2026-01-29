import arcade
import math
import random
from Animation import AnimatedSprite

GRID_TILE_SIZE = 32
DETECTION_RADIUS = 6 * GRID_TILE_SIZE
LOSE_RADIUS = 7 * GRID_TILE_SIZE 


class Enemy1(AnimatedSprite):
    def __init__(self, target_player, map_width, map_height):
        super().__init__("res/enemy1.png", scale=1.0)
        self.player = target_player
        self.speed = 1.5
        self.barrier_list = None 
        self.path = []
        self.map_width = map_width
        self.map_height = map_height
        self.vision_time = 0
        self.wander_time = 0
        self.health = 2

    def update(self, delta_time: float):
        self.vision_time -= delta_time
        can_see = False
        if self.vision_time <= 0:
            self.vision_time = 0.2
            can_see = arcade.has_line_of_sight(
                self.position,
                self.player.position,
                self.barrier_list.blocking_sprites,
                max_distance=DETECTION_RADIUS)
            self.can_see_player = can_see
        if self.can_see_player:
            self.path = []
            self.move_straight(self.player.position)
        else:
            self.update_wander(delta_time)
            self.move_along_path()

    def move_straight(self, target_pos):
        dx = target_pos[0] - self.center_x
        dy = target_pos[1] - self.center_y
        dist = math.hypot(dx, dy)
        if dist > self.speed:
            self.center_x += (dx / dist) * self.speed
            self.center_y += (dy / dist) * self.speed

    def update_wander(self, delta_time):
        self.wander_time -= delta_time
        if not self.path or self.wander_time <= 0:
            self.wander_time = random.uniform(4.0, 8.0)
            dx = random.randint(100, self.map_width - 100)
            dy = random.randint(100, self.map_height - 100)
            self.path = arcade.astar_calculate_path(
                self.position,
                (dx, dy),
                self.barrier_list,
                diagonal_movement=True)

    def move_along_path(self):
        if not self.path:
            return
        next_point = self.path[0]
        dx = next_point[0] - self.center_x
        dy = next_point[1] - self.center_y
        dist = math.hypot(dx, dy)
        if dist > self.speed:
            self.center_x += (dx / dist) * self.speed
            self.center_y += (dy / dist) * self.speed
        else:
            if len(self.path) > 0:
                self.path.pop(0)


class Enemy2(AnimatedSprite):
    def __init__(self, target_player, map_width, map_height, bullet_list):
        super().__init__("res/enemy2.png", scale=1.0)
        self.player = target_player
        self.bullet_list = bullet_list
        self.speed = 0.6
        self.barrier_list = None
        self.path = []
        self.map_width = map_width
        self.map_height = map_height

        self.bs = arcade.load_sound("res/shoot-e.mp3")

        self.vision_time = 0
        self.wander_time = 0
        self.shoot_timer = 0
        self.health = 7
        self.can_see_player = False

    def update(self, delta_time: float):
        self.vision_time -= delta_time
        self.shoot_timer -= delta_time

        if self.vision_time <= 0:
            self.vision_time = 0.2
            self.can_see_player = arcade.has_line_of_sight(
                self.position,
                self.player.position,
                self.barrier_list.blocking_sprites,
                max_distance=500)

        if self.can_see_player:
            if not self.path:
                rx = self.center_x + random.randint(-200, 200)
                ry = self.center_y + random.randint(-200, 200)
                rx = max(100, min(rx, self.map_width - 100))
                ry = max(100, min(ry, self.map_height - 100))
                self.path = arcade.astar_calculate_path(self.position, (rx, ry), self.barrier_list)

            self.move_along_path()

            if self.shoot_timer <= 0:
                self.shoot()
                self.shoot_timer = 1.5
        else:
            self.update_wander(delta_time)
            self.move_along_path()

    def move_straight(self, target_pos, reverse=False):
        dx = target_pos[0] - self.center_x
        dy = target_pos[1] - self.center_y
        dist = math.hypot(dx, dy)

        if dist > 0:
            multiplier = -1 if reverse else 1
            step_x = (dx / dist) * self.speed * multiplier
            step_y = (dy / dist) * self.speed * multiplier

            self.center_x += step_x
            if arcade.check_for_collision_with_list(self, self.barrier_list.blocking_sprites):
                self.center_x -= step_x

            self.center_y += step_y
            if arcade.check_for_collision_with_list(self, self.barrier_list.blocking_sprites):
                self.center_y -= step_y

    def shoot(self):
        bullet = arcade.Sprite("res/ally_bullet2.png", 1.2)
        arcade.play_sound(self.bs)
        bullet.position = self.position
        bullet.owner = "enemy"
        bullet.damage = 1

        angle = math.atan2(self.player.center_y - self.center_y,
                           self.player.center_x - self.center_x)

        bullet.change_x = math.cos(angle) * 2
        bullet.change_y = math.sin(angle) * 2
        bullet.angle = math.degrees(angle) - 90

        self.bullet_list.append(bullet)

    def update_wander(self, delta_time):
        self.wander_time -= delta_time
        if not self.path or self.wander_time <= 0:
            self.wander_time = random.uniform(4.0, 8.0)
            dx = random.randint(100, self.map_width - 100)
            dy = random.randint(100, self.map_height - 100)
            self.path = arcade.astar_calculate_path(
                self.position,
                (dx, dy),
                self.barrier_list,
                diagonal_movement=True)

    def move_along_path(self):
        if not self.path:
            return
        next_point = self.path[0]
        dx = next_point[0] - self.center_x
        dy = next_point[1] - self.center_y
        dist = math.hypot(dx, dy)

        if dist > self.speed:
            step_x = (dx / dist) * self.speed
            step_y = (dy / dist) * self.speed

            self.center_x += step_x
            if arcade.check_for_collision_with_list(self, self.barrier_list.blocking_sprites):
                self.center_x -= step_x
                self.path = []

            self.center_y += step_y
            if arcade.check_for_collision_with_list(self, self.barrier_list.blocking_sprites):
                self.center_y -= step_y
                self.path = []
        else:
            if len(self.path) > 0:
                self.path.pop(0)

class BossChaser(AnimatedSprite):
    def __init__(self, player, map_width, map_height):
        super().__init__("res/Boss1.png", scale=1.5)
        self.player = player
        self.map_width = map_width
        self.map_height = map_height
        self.hp = 30
        self.health = self.hp
        self.speed = player.speed * 1.05
        self.portal_spawned = False

    def update(self, delta_time):

        dx = self.player.center_x - self.center_x
        dy = self.player.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.center_x += (dx / dist) * self.speed
            self.center_y += (dy / dist) * self.speed

    def take_damage(self, amount, game_view):
        self.hp -= amount
        if self.hp <= 0 and not self.portal_spawned:
            self.die(game_view)

    def die(self, game_view):
        for _ in range(15):
            particle = arcade.SpriteCircle(4, arcade.color.ORANGE)
            particle.center_x = self.center_x
            particle.center_y = self.center_y
            particle.change_x = random.uniform(-2, 2)
            particle.change_y = random.uniform(-2, 2)
            game_view.particle_list.append(particle)

        portal_list = game_view.tile_map.sprite_lists.get("portal_layer")
        if portal_list:
            for portal_sprite in portal_list:
                portal_sprite.center_x = self.center_x
                portal_sprite.center_y = self.center_y
                portal_sprite.portal = True
                game_view.enemy_list.append(portal_sprite)
        self.portal_spawned = True
        self.remove_from_sprite_lists()

class BossShooter(AnimatedSprite):
    def __init__(self, player, bullet_list, map_width, map_height):
        super().__init__("res/Boss2.png", scale=1.5)
        self.player = player
        self.bullet_list = bullet_list
        self.map_width = map_width
        self.map_height = map_height
        self.hp = 12
        self.health = self.hp  
        self.speed = 0.5
        self.shoot_timer = 1
        self.wander_time = 0
        self.portal_spawned = False

    def update(self, delta_time):
        self.shoot_timer -= delta_time
        self.wander_time -= delta_time

        if not hasattr(self, "target") or self.wander_time <= 0:
            self.wander_time = random.uniform(3.0, 6.0)
            self.target = (random.randint(100, self.map_width - 100),
                           random.randint(100, self.map_height - 100))
        if self.target is None:
            return
        dx = self.target[0] - self.center_x
        dy = self.target[1] - self.center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            step = min(self.speed, dist)
            self.center_x += dx / dist * step
            self.center_y += dy / dist * step
        if dist < 5:
            self.target = None

        dxp = self.player.center_x - self.center_x
        dyp = self.player.center_y - self.center_y
        distp = math.hypot(dxp, dyp)
        if distp < DETECTION_RADIUS and self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = 1.5

    def shoot(self):
        for i in range(-1, 2):
            angle = math.atan2(self.player.center_y - self.center_y,
                               self.player.center_x - self.center_x) + i * 0.1
            bullet = arcade.Sprite("res/ally_bullet2.png", scale=1.0)
            bullet.center_x = self.center_x
            bullet.center_y = self.center_y
            bullet.change_x = math.cos(angle)
            bullet.change_y = math.sin(angle)
            bullet.damage = 2
            bullet.owner = "enemy"
            self.bullet_list.append(bullet)

    def take_damage(self, amount, game_view):
        self.hp -= amount
        if self.hp <= 0 and not self.portal_spawned:
            self.die(game_view)

    def die(self, game_view):
        for _ in range(15):
            particle = arcade.SpriteCircle(4, arcade.color.ORANGE)
            particle.center_x = self.center_x
            particle.center_y = self.center_y
            particle.change_x = random.uniform(-2, 2)
            particle.change_y = random.uniform(-2, 2)
            game_view.particle_list.append(particle)

        portal_list = game_view.tile_map.sprite_lists.get("portal_layer")
        if portal_list:
            for portal_sprite in portal_list:
                portal_sprite.center_x = self.center_x
                portal_sprite.center_y = self.center_y
                portal_sprite.portal = True
                game_view.enemy_list.append(portal_sprite)
        self.portal_spawned = True
        self.remove_from_sprite_lists()