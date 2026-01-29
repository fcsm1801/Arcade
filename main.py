import arcade
from arcade import *
import math
import random
from enemies import Enemy1, Enemy2, BossChaser, BossShooter
from Animation import AnimatedSprite
from pyglet.graphics import Batch
from arcade.gui import UIManager, UITextureButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from arcade.particles import Emitter, EmitBurst, FadeParticle

SPARK_TEX = [
    arcade.make_soft_circle_texture(8, arcade.color.PASTEL_YELLOW),
    arcade.make_soft_circle_texture(8, arcade.color.PEACH),
    arcade.make_soft_circle_texture(8, arcade.color.BABY_BLUE),
    arcade.make_soft_circle_texture(8, arcade.color.ELECTRIC_CRIMSON),
]
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 1024
SCREEN_TITLE = "Game"
GRID_TILE_SIZE = 32
TILE_SCALING = 1.0


class DeathView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.batch = Batch()
        self.pause_text = UILabel(text="Конец игры",
                                  font_size=100,
                                  text_color=arcade.color.WHITE,
                                  width=700,
                                  align="center")
        self.background_color = arcade.color.BLUE_GRAY
        self.manager = UIManager()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=20)

        texture_normal = arcade.load_texture(":resources:/gui_basic_assets/button/red_normal.png")
        texture_hovered = arcade.load_texture(":resources:/gui_basic_assets/button/red_hover.png")
        texture_pressed = arcade.load_texture(":resources:/gui_basic_assets/button/red_press.png")

        b_s = UITextureButton(texture=texture_normal,
                              text='Сохранить результаты',
                              texture_hovered=texture_hovered,
                              texture_pressed=texture_pressed,
                              scale=1.0)
        b_s.on_click = self.save_g

        b_e = UITextureButton(texture=texture_normal,
                              text='Выйти в меню',
                              texture_hovered=texture_hovered,
                              texture_pressed=texture_pressed,
                              scale=1.0)
        b_e.on_click = self.return_g

        self.box_layout.add(self.pause_text)
        self.box_layout.add(b_s)
        self.box_layout.add(b_e)

        self.anchor_layout.add(
            child=self.box_layout,
            anchor_x="center_x",
            anchor_y="center_y"
        )

        self.manager.add(self.anchor_layout)

    def on_show_view(self):
        self.manager.enable()
        self.window.set_mouse_visible(True)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def save_g(self, event):
        stat = {}
        try:
            with open('player_stat.txt', 'r') as f:
                for line in f:
                    if '=' in line:
                        name, value = line.strip().split('=')
                        stat[name] = int(value)
        except FileNotFoundError:
            stat = {'max_loop': 0}

        current_loop = self.game_view.player.loop

        if current_loop > stat.get('max_loop', 0):
            stat['max_loop'] = current_loop

        with open('player_stat.txt', 'w') as f:
            for name, value in stat.items():
                f.write(f"{name}={value}\n")

        game_view = MenuView()
        self.window.show_view(game_view)

    def return_g(self, event):
        game_view = MenuView()
        self.window.show_view(game_view)


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.batch = Batch()
        self.pause_text = UILabel(text="Пауза",
                                  font_size=100,
                                  text_color=arcade.color.WHITE,
                                  width=700,
                                  align="center")
        self.background_color = arcade.color.BLUE_GRAY
        self.manager = UIManager()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=20)

        texture_normal = arcade.load_texture(":resources:/gui_basic_assets/button/red_normal.png")
        texture_hovered = arcade.load_texture(":resources:/gui_basic_assets/button/red_hover.png")
        texture_pressed = arcade.load_texture(":resources:/gui_basic_assets/button/red_press.png")

        b_s = UITextureButton(texture=texture_normal,
                              text='Продолжить',
                              texture_hovered=texture_hovered,
                              texture_pressed=texture_pressed,
                              scale=1.0)
        b_s.on_click = self.cont_g

        b_e = UITextureButton(texture=texture_normal,
                              text='Выйти в меню',
                              texture_hovered=texture_hovered,
                              texture_pressed=texture_pressed,
                              scale=1.0)
        b_e.on_click = self.return_g

        self.box_layout.add(self.pause_text)
        self.box_layout.add(b_s)
        self.box_layout.add(b_e)

        self.anchor_layout.add(
            child=self.box_layout,
            anchor_x="center_x",
            anchor_y="center_y"
        )

        self.manager.add(self.anchor_layout)

    def on_show_view(self):
        self.manager.enable()
        self.window.set_mouse_visible(True)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def cont_g(self, event):
        self.window.show_view(self.game_view)

    def return_g(self, event):
        game_view = MenuView()
        self.window.show_view(game_view)


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLUE_GRAY
        self.manager = arcade.gui.UIManager(window=self.window)

        self.emitters = []

        self.menus = arcade.load_sound('res/menu.mp3')
        self.m_p = None

        self.batch = Batch()
        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=20)

        texture_normal = arcade.load_texture(":resources:/gui_basic_assets/button/red_normal.png")
        texture_hovered = arcade.load_texture(":resources:/gui_basic_assets/button/red_hover.png")
        texture_pressed = arcade.load_texture(":resources:/gui_basic_assets/button/red_press.png")

        main_t = UILabel(text="Крутая игра 3d",
                         font_size=100,
                         text_color=arcade.color.WHITE,
                         width=700,
                         align="center")

        b_s = UITextureButton(texture=texture_normal,
                              text='Новый забег',
                              texture_hovered=texture_hovered,
                              texture_pressed=texture_pressed,
                              scale=1.0)
        b_s.on_click = self.start_game

        b_e = UITextureButton(texture=texture_normal,
                              text='Выйти из игры',
                              texture_hovered=texture_hovered,
                              texture_pressed=texture_pressed,
                              scale=1.0)
        b_e.on_click = self.close_game

        self.box_layout.add(main_t)
        self.box_layout.add(b_s)
        self.box_layout.add(b_e)

        self.anchor_layout.add(
            child=self.box_layout,
            anchor_x="center_x",
            anchor_y="center_y"
        )

        self.manager.add(self.anchor_layout)

    def on_show_view(self):
        self.manager.enable()
        self.window.set_mouse_visible(True)
        if not self.m_p:
            self.m_p = arcade.play_sound(self.menus, loop=True)

    def on_hide_view(self):
        self.manager.disable()
        if self.m_p:
            arcade.stop_sound(self.m_p)
            self.m_p = None

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def start_game(self, event):
        game_view = GameView()
        game_view.setup(reset_progress=True)
        self.window.show_view(game_view)

    def close_game(self, event):
        arcade.exit()


class Loot(arcade.Sprite):
    def __init__(self, loot_type, x, y):
        self.type = loot_type
        img = f"res/item{loot_type}.png"
        super().__init__(img, scale=1.0, center_x=x, center_y=y)

    def apply_bonus(self, player):
        if self.type == "2":
            player.max_health += 5
            player.health = player.max_health
        elif self.type == "3":
            player.speed += 0.02
        elif self.type == "1":
            player.damage += 2


class Cross(arcade.Sprite):
    def __init__(self):
        super().__init__("res/cross.png", scale=1.0)


class Player(AnimatedSprite):
    def __init__(self):
        super().__init__("res/player.png", scale=1.0)
        self.health = 10
        self.max_health = 10
        self.speed = 0.15
        self.hit_cooldown = 0
        self.current_level = 1
        self.loop = 0
        self.damage = 3


class Bullet(arcade.Sprite):
    def __init__(self, x, y, change_x, change_y, damage):
        super().__init__("res/ally_bullet2.png", scale=1.0)
        self.center_x = x
        self.center_y = y
        self.change_x = change_x
        self.change_y = change_y
        self.damage = damage
        self.owner = "player"

    def on_update(self, delta_time: float):
        self.center_x += self.change_x
        self.center_y += self.change_y


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.window.set_mouse_visible(False)
        self.invincibility_timer = 0.0
        self.emitters = []

        self.hurt = arcade.load_sound("res/hurt-a.mp3")
        self.ghost_sound = arcade.load_sound("res/ghost_death.mp3")
        self.bullet_sound = arcade.load_sound("res/shoot-a.mp3")
        self.move = arcade.load_sound("res/move-d.mp3")

        self.score = 0

        self.fps_timer = 0
        self.fps_frames = 0

        self.shoot_cooldown = 0.8
        self.shoot_timer = 0.0
        self.friction = 0.93

        self.bullet_list = None
        self.enemy_list = None
        self.player_list = None
        self.frame_count = 0

        self.speed = 1
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)
        self.camera = arcade.camera.Camera2D()

        self.player = Player()

        self.mouse_x = 0
        self.mouse_y = 0
        self.cross_offset = 40
        self.zoom = 3.44

    def setup(self, reset_progress=False):
        if reset_progress:
            self.player.current_level = 1
            self.player.loop = 0
            self.player.health = self.player.max_health
        self.invincibility_timer = 3.0

        self.particle_list = None
        self.portal_list = None
        self.loot_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.loot_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        stat = {}
        try:
            with open('player_stat.txt', 'r') as f:
                for line in f:
                    if '=' in line:
                        name, value = line.strip().split('=')
                        stat[name] = int(value)
        except FileNotFoundError:
            stat = {'max_loop': 0}

        current_loop = self.player.loop
        if current_loop > stat.get('max_loop', 0):
            stat['max_loop'] = current_loop
        with open('player_stat.txt', 'w') as f:
            for name, value in stat.items():
                f.write(f"{name}={value}\n")

        levels = {
            1: ['rooms/lvl1_v1.tmx', 'rooms/lvl1_v2.tmx', 'rooms/lvl1_v3.tmx'],
            2: ['rooms/lvl2_v1.tmx'],
            3: ['rooms/lvl3_v1.tmx']
        }

        map_name = random.choice(levels[self.player.current_level])

        self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        if "portal_layer" in self.tile_map.sprite_lists:
            self.portal_list = self.tile_map.sprite_lists["portal_layer"]
            for portal in self.portal_list:
                portal.visible = True
        else:
            self.portal_list = arcade.SpriteList(use_spatial_hash=True)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.ground_list = arcade.SpriteList(use_spatial_hash=True)
        self.object_list = arcade.SpriteList(use_spatial_hash=True)
        self.door_list = arcade.SpriteList(use_spatial_hash=True)

        self.wall_list.extend(self.tile_map.sprite_lists["walls"])
        self.ground_list.extend(self.tile_map.sprite_lists["ground"])
        self.object_list.extend(self.tile_map.sprite_lists["obj"])
        self.door_list.extend(self.tile_map.sprite_lists['ex_coll'])

        self.f_wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.f_wall_list.extend(self.wall_list)
        self.f_wall_list.extend(self.object_list)

        map_w = self.tile_map.width * self.tile_map.tile_width
        map_h = self.tile_map.height * self.tile_map.tile_height
        self.player.center_x = map_w / 2
        self.player.center_y = (map_h / 2) - 50
        self.player_list.append(self.player)

        if self.player.left < 0:
            self.player.left = 0
        elif self.player.right > map_w:
            self.player.right = map_w

        if self.player.bottom < 0:
            self.player.bottom = 0
        elif self.player.top > map_h:
            self.player.top = map_h

        if self.player.current_level == 1:
            self.object1_list = arcade.SpriteList(use_spatial_hash=True)
            self.h_obj = arcade.SpriteList(use_spatial_hash=True)

            self.object1_list.extend(self.tile_map.sprite_lists["obj1"])
            self.h_obj.extend(self.tile_map.sprite_lists["hit_obj"])

            for sprite in self.door_list:
                sprite.visible = False

            self.bullet_list = arcade.SpriteList()
            self.cross_list = arcade.SpriteList()
            self.cross = Cross()
            self.cross_list.append(self.cross)

            self.f_wall_list.extend(self.h_obj)
            self.enemy_list = arcade.SpriteList()
            self.bullet_list = arcade.SpriteList()

            spawned_e1 = False
            while not spawned_e1:
                e1 = Enemy1(self.player, map_w, map_h)
                e1.center_x = random.randint(100, map_w - 100)
                e1.center_y = random.randint(100, map_h - 100)
                if not arcade.check_for_collision_with_list(e1, self.f_wall_list):
                    self.enemy_list.append(e1)
                    spawned_e1 = True

            spawned_e2 = False
            while not spawned_e2:
                e2 = Enemy2(self.player, map_w, map_h, self.bullet_list)
                e2.center_x = random.randint(100, map_w - 100)
                e2.center_y = random.randint(100, map_h - 100)
                if not arcade.check_for_collision_with_list(e2, self.f_wall_list):
                    self.enemy_list.append(e2)
                    spawned_e2 = True

            spawned_e3 = False
            while not spawned_e3:
                e3 = Enemy1(self.player, map_w, map_h)
                e3.center_x = random.randint(100, map_w - 100)
                e3.center_y = random.randint(100, map_h - 100)
                if not arcade.check_for_collision_with_list(e3, self.f_wall_list):
                    self.enemy_list.append(e3)
                    spawned_e3 = True

            spawned_e4 = False
            while not spawned_e4:
                e4 = Enemy1(self.player, map_w, map_h)
                e4.center_x = random.randint(100, map_w - 100)
                e4.center_y = random.randint(100, map_h - 100)
                if not arcade.check_for_collision_with_list(e4, self.f_wall_list):
                    self.enemy_list.append(e4)
                    spawned_e4 = True

            self.barrier_list = arcade.AStarBarrierList(
                self.player,
                self.f_wall_list,
                GRID_TILE_SIZE,
                0, map_w,
                0, map_h
            )

            for enemy in self.enemy_list:
                enemy.barrier_list = self.barrier_list

            self.physics_engine = arcade.PhysicsEngineSimple(
                self.player, [self.wall_list, self.object_list, self.h_obj]
            )

        elif self.player.current_level == 2:
            self.chest = arcade.SpriteList(use_spatial_hash=True)
            self.object1_list = arcade.SpriteList(use_spatial_hash=True)

            self.object1_list.extend(self.tile_map.sprite_lists["obj1"])
            self.chest.extend(self.tile_map.sprite_lists["chest"])

            self.bullet_list = arcade.SpriteList()
            self.cross_list = arcade.SpriteList()
            self.cross = Cross()
            self.cross_list.append(self.cross)

            self.enemy_list = arcade.SpriteList()
            self.bullet_list = arcade.SpriteList()

            self.barrier_list = arcade.AStarBarrierList(
                self.player,
                self.f_wall_list,
                GRID_TILE_SIZE,
                0, map_w,
                0, map_h
            )

            self.physics_engine = arcade.PhysicsEngineSimple(
                self.player, [self.wall_list, self.object_list]
            )

        elif self.player.current_level == 3:
            self.object1_list = arcade.SpriteList(use_spatial_hash=True)
            self.h_obj = arcade.SpriteList(use_spatial_hash=True)

            self.object1_list.extend(self.tile_map.sprite_lists["obj1"])
            self.h_obj.extend(self.tile_map.sprite_lists["hit_obj"])

            for sprite in self.door_list:
                sprite.visible = False

            self.bullet_list = arcade.SpriteList()
            self.cross_list = arcade.SpriteList()
            self.cross = Cross()
            self.cross_list.append(self.cross)

            self.f_wall_list.extend(self.h_obj)

            self.enemy_list = arcade.SpriteList()
            self.bullet_list = arcade.SpriteList()

            spawned_e1 = False
            while not spawned_e1:
                e1 = Enemy1(self.player, map_w, map_h)
                e1.center_x = random.randint(100, map_w - 100)
                e1.center_y = random.randint(100, map_h - 100)
                if not arcade.check_for_collision_with_list(e1, self.f_wall_list):
                    self.enemy_list.append(e1)
                    spawned_e1 = True

            spawned_e2 = False
            while not spawned_e2:
                e2 = Enemy2(self.player, map_w, map_h, self.bullet_list)
                e2.center_x = random.randint(100, map_w - 100)
                e2.center_y = random.randint(100, map_h - 100)
                if not arcade.check_for_collision_with_list(e2, self.f_wall_list):
                    self.enemy_list.append(e2)
                    spawned_e2 = True

            spawned_e3 = False
            attempt = 0
            while not spawned_e3 and attempt < 100:
                e3 = random.choice(
                    [BossChaser(self.player, map_w, map_h), BossShooter(self.player, self.bullet_list, map_w, map_h)])
                e3.center_x = random.randint(100, map_w - 100)
                e3.center_y = random.randint(100, map_h - 100)
                if not arcade.check_for_collision_with_list(e3, self.f_wall_list):
                    self.enemy_list.append(e3)
                    spawned_e3 = True
                attempt += 1

            self.barrier_list = arcade.AStarBarrierList(
                self.player,
                self.f_wall_list,
                GRID_TILE_SIZE,
                0, map_w,
                0, map_h
            )

            for enemy in self.enemy_list:
                enemy.barrier_list = self.barrier_list

            self.physics_engine = arcade.PhysicsEngineSimple(
                self.player, [self.wall_list, self.object_list, self.h_obj]
            )

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.camera.zoom = self.zoom

        self.ground_list.draw(pixelated=True)
        self.wall_list.draw(pixelated=True)
        self.object_list.draw(pixelated=True)

        if self.enemy_list:
            self.enemy_list.draw(pixelated=True)

        self.object1_list.draw(pixelated=True)
        self.player_list.draw(pixelated=True)
        self.bullet_list.draw(pixelated=True)
        self.door_list.draw(pixelated=True)

        for e in self.emitters:
            e.draw()

        if self.player.current_level == 1 or self.player.current_level == 3:
            self.h_obj.draw(pixelated=True)
        elif self.player.current_level == 2:
            self.chest.draw(pixelated=True)
            self.loot_list.draw(pixelated=True)

        if not self.enemy_list:
            self.portal_list.draw(pixelated=True)

        self.cross_list.draw(pixelated=True)

        start_x = 300
        start_y = 300
        bar_max_width = 200
        bar_height = 20

        health_ratio = int(self.player.health / self.player.max_health)
        current_width = int(bar_max_width * health_ratio)

        arcade.draw_rect_outline(
            arcade.rect.XYWH(x=start_x + bar_max_width / 2, y=start_y, width=bar_max_width, height=bar_height),
            color=arcade.color.BLACK
        )

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x=start_x + current_width / 2, y=start_y, width=current_width, height=bar_height),
            color=arcade.color.MAROON
        )

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x=start_x + current_width / 2, y=start_y, width=current_width, height=bar_height),
            arcade.color.APPLE_GREEN
        )

        arcade.draw_text(f"HP: {self.player.health}/{self.player.max_health}",
                         start_x + 5, start_y - 7, arcade.color.WHITE, 12, bold=True)

    def on_update(self, delta_time: float):
        if self.particle_list:
            self.particle_list.update()
        self.bullet_list.update()
        self.portal_list.update()
        self.player_list.update_animation(delta_time)
        self.player_list.update()

        if self.invincibility_timer > 0:
            self.invincibility_timer -= delta_time

        if self.enemy_list:
            self.enemy_list.update_animation(delta_time)
            self.enemy_list.update()

        if self.player.current_level == 2:
            self.chest.update_animation(delta_time)
            chests_hit = arcade.check_for_collision_with_list(self.player, self.chest)
            for chest in chests_hit:
                loot_type = str(random.choice([1, 2, 3]))
                item = Loot(loot_type, chest.center_x, chest.center_y)
                self.loot_list.append(item)
                chest.remove_from_sprite_lists()

        emitters_copy = self.emitters.copy()
        for e in emitters_copy:
            e.update(int(delta_time))

        hit_loot = arcade.check_for_collision_with_list(self.player, self.loot_list)
        for item in hit_loot:
            item.apply_bonus(self.player)
            item.remove_from_sprite_lists()

        if self.enemy_list is not None and len(self.enemy_list) == 0:
            for sprite in self.door_list:
                sprite.visible = True
            if self.door_list:
                door_target = self.door_list[0]
                dist = arcade.get_distance_between_sprites(self.player, door_target)
                if dist < 160:
                    self.door_list.update_animation(delta_time)
                if dist < 10:
                    self.next_level()

        if self.up_pressed:
            self.player.change_y += self.player.speed
        if self.down_pressed:
            self.player.change_y -= self.player.speed
        if self.left_pressed:
            self.player.change_x -= self.player.speed
        if self.right_pressed:
            self.player.change_x += self.player.speed

        self.player.change_x *= self.friction
        self.player.change_y *= self.friction

        if abs(self.player.change_x) < 0.05:
            self.player.change_x = 0
        if abs(self.player.change_y) < 0.05:
            self.player.change_y = 0

        self.frame_count += 1

        if self.shoot_timer > 0:
            self.shoot_timer -= delta_time

        self.physics_engine.update()
        self.bullet_list.update()

        if self.enemy_list:
            self.enemy_list.update()

        self.camera.position = ((self.tile_map.width * self.tile_map.tile_width) / 2,
                                (self.tile_map.height * self.tile_map.tile_height) / 2)

        mouse_pos = self.camera.unproject((self.mouse_x, self.mouse_y))
        diff_x = mouse_pos[0] - self.player.center_x
        diff_y = mouse_pos[1] - self.player.center_y
        dist = math.sqrt(diff_x ** 2 + diff_y ** 2)

        if self.player.hit_cooldown > 0:
            self.player.hit_cooldown -= delta_time

        if self.player.health <= 0:
            self.window.show_view(DeathView(self))

        if self.enemy_list:
            hit_enemies = arcade.check_for_collision_with_list(self.player, self.enemy_list)
            for enemy in hit_enemies:
                if self.player.hit_cooldown <= 0:
                    self.player.health -= 3
                    self.player.hit_cooldown = 1.5

                    dx = self.player.center_x - enemy.center_x
                    dy = self.player.center_y - enemy.center_y
                    dist_to_enemy = math.hypot(dx, dy)

                    knockback_force = 2

                    if dist_to_enemy > 0:
                        self.player.change_x += (dx / dist_to_enemy) * knockback_force
                        self.player.change_y += (dy / dist_to_enemy) * knockback_force

        if dist > 0:
            self.cross.center_x = self.player.center_x + (diff_x / dist) * self.cross_offset
            self.cross.center_y = self.player.center_y + (diff_y / dist) * self.cross_offset

        for bullet in self.bullet_list:
            hit_walls = arcade.check_for_collision_with_list(bullet,
                                                             self.wall_list) or arcade.check_for_collision_with_list(
                bullet, self.object_list)
            non_breakable_obj = arcade.check_for_collision_with_list(bullet, self.object_list)

            if self.player.current_level == 1 or self.player.current_level == 3:
                hit_objects = arcade.check_for_collision_with_list(bullet, self.h_obj)
                for obj in hit_objects:
                    extra_parts = arcade.get_sprites_at_point((obj.position[0], obj.position[1] + 16),
                                                              self.object1_list)
                    for part in extra_parts:
                        part.remove_from_sprite_lists()

                    obj.remove_from_sprite_lists()
                    if self.enemy_list:
                        self.barrier_list.recalculate()

            hit_enemies = arcade.check_for_collision_with_list(self.player, self.enemy_list)
            for enemy in hit_enemies:
                if self.invincibility_timer <= 0:
                    player_hit = arcade.check_for_collision_with_list(self.player, self.bullet_list)
                    for bullet in player_hit:
                        if bullet.owner == "enemy":
                            self.player.health -= bullet.damage
                            arcade.play_sound(self.hurt)
                            bullet.remove_from_sprite_lists()
                elif self.player.hit_cooldown <= 0:
                    self.player.health -= 3
                    arcade.play_sound(self.hurt)
                    if self.player.health <= 0:
                        DeathView(self)
                    self.player.hit_cooldown = 1.5

                    dx = self.player.center_x - enemy.center_x
                    dy = self.player.center_y - enemy.center_y
                    dist = math.hypot(dx, dy)

                    knockback_force = 2

                    if dist > 0:
                        self.player.change_x += (dx / dist) * knockback_force
                        self.player.change_y += (dy / dist) * knockback_force

            if dist > 0:
                self.cross.center_x = self.player.center_x + (diff_x / dist) * self.cross_offset
                self.cross.center_y = self.player.center_y + (diff_y / dist) * self.cross_offset

            for bullet in self.bullet_list:
                hit_objects = arcade.check_for_collision_with_list(bullet, self.h_obj)
                if hit_objects:
                    for obj in hit_objects:
                        extra_parts = arcade.get_sprites_at_point((obj.position[0], obj.position[1] + 16),
                                                                  self.object1_list)
                        for part in extra_parts:
                            part.remove_from_sprite_lists()

                        obj.remove_from_sprite_lists()
                        self.barrier_list.recalculate()

                    bullet.remove_from_sprite_lists()
                    continue

                if arcade.check_for_collision_with_list(bullet, self.wall_list) or \
                        arcade.check_for_collision_with_list(bullet, self.object_list):
                    bullet.remove_from_sprite_lists()
                    continue

                if getattr(bullet, 'owner', '') == "enemy":
                    if arcade.check_for_collision(bullet, self.player):
                        if self.invincibility_timer <= 0:
                            player_hit = arcade.check_for_collision_with_list(self.player, self.bullet_list)
                            for bullet in player_hit:
                                if bullet.owner == "enemy":
                                    self.player.health -= bullet.damage
                                    arcade.play_sound(self.hurt)
                                    bullet.remove_from_sprite_lists()
                        elif self.player.hit_cooldown <= 0:
                            self.player.health -= 1
                            arcade.play_sound(self.hurt)
                            self.player.hit_cooldown = 0.5
                            bullet.remove_from_sprite_lists()
                            if self.player.health <= 0:
                                DeathView(self)
                        continue

                if getattr(bullet, 'owner', '') == "player":
                    hit_enemies = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                    if hit_enemies:
                        for enemy in hit_enemies:
                            enemy.health -= getattr(bullet, 'damage', 1)
                            if enemy.health <= 0:
                                self.emitters.append(make_explosion(enemy.center_x, enemy.center_y))
                                enemy.remove_from_sprite_lists()
                                self.score += 1
                            break
                        bullet.remove_from_sprite_lists()

        if self.enemy_list:
            for sprite in self.enemy_list:
                if getattr(sprite, "portal", False):
                    sprite.update_animation(delta_time)
                    if arcade.check_for_collision(self.player, sprite):
                        self.player.loop += 1
                        self.next_level()

        if self.portal_list:
            portal_target = self.portal_list[0]
            dist = arcade.get_distance_between_sprites(self.player, portal_target)
            if dist < 10:
                self.next_level()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def next_level(self):
        if self.player.current_level == 3:
            self.player.loop += 1
            self.player.current_level = 1
        else:
            self.player.current_level += 1
        self.setup()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.ESCAPE:
            pause_view = PauseView(self)
            self.window.show_view(pause_view)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.shoot_timer <= 0:
                dx = self.cross.center_x - self.player.center_x
                dy = self.cross.center_y - self.player.center_y
                dist = math.sqrt(dx ** 2 + dy ** 2)

                if dist > 0:
                    bullet_speed = self.player.damage
                    bullet = Bullet(
                        self.player.center_x, self.player.center_y,
                        (dx / dist) * bullet_speed,
                        (dy / dist) * bullet_speed,
                        bullet_speed
                    )
                    self.bullet_list.append(bullet)
                    arcade.play_sound(self.bullet_sound)

                    self.shoot_timer = self.shoot_cooldown


def make_explosion(x, y, count=20):
    return Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(count),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=random.choice(SPARK_TEX),
            change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
            lifetime=random.uniform(0.5, 1.1),
            start_alpha=255, end_alpha=0,
            scale=random.uniform(0.35, 0.6),
            mutation_callback=gravity_drag,
        ),
    )


def gravity_drag(p):
    p.change_y += -0.03
    p.change_x *= 0.92
    p.change_y *= 0.92


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
