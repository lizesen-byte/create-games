import os
from ursina import *
from random import uniform

app = Ursina()

window.title = "Cyber Robot Wars"

laser_sound_path = None
for ext in ('wav', 'ogg'):
    candidate = os.path.join(os.path.dirname(__file__), f'laser.{ext}')
    if os.path.exists(candidate):
        laser_sound_path = candidate
        break

boss_fire_sound = None
if laser_sound_path is not None:
    try:
        boss_fire_sound = Audio(laser_sound_path, loop=False, autoplay=False)
    except Exception:
        boss_fire_sound = None

transform_sound_path = None
for ext in ('wav', 'ogg'):
    candidate = os.path.join(os.path.dirname(__file__), f'transform.{ext}')
    if os.path.exists(candidate):
        transform_sound_path = candidate
        break

transform_sound = None
if transform_sound_path is not None:
    try:
        transform_sound = Audio(transform_sound_path, loop=False, autoplay=False)
    except Exception:
        transform_sound = None

# ---------- PLAYER ----------

class Bullet(Entity):
    def __init__(self, position, direction, color=color.yellow, speed=30, damage=20):
        super().__init__(
            model='sphere',
            color=color,
            emissive_color=rgb(255,255,180),
            texture='white_cube',
            scale=.25,
            position=position
        )
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        destroy(self, 3)

    def update(self):
        self.position += self.direction * self.speed * time.dt

        for enemy in enemies[:]:
            if distance(self, enemy) < 1.2:
                enemy.health -= self.damage
                destroy(self)

                if enemy.health <= 0:
                    destroy(enemy)
                    enemies.remove(enemy)
                    player.xp += 10
                return


class Missile(Bullet):
    def __init__(self, position, direction):
        super().__init__(position, direction, color=color.azure, speed=24, damage=40)
        self.model = 'cone'
        self.emissive_color = color.cyan
        self.scale = .35


class EnemyBullet(Entity):
    def __init__(self, position, direction, speed=20, damage=15):
        super().__init__(
            model='sphere',
            color=rgb(255,100,255),
            emissive_color=rgb(255,140,255),
            scale=.35,
            position=position
        )
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        destroy(self, 4)

    def update(self):
        self.position += self.direction * self.speed * time.dt

        if distance(self, player) < 1.2:
            player.health -= self.damage
            destroy(self)


class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.rgba(0,0,0,0),
            position=(0,1,0),
            scale=Vec3(1,2,1)
        )

        self.mode = "robot"
        self.speed = 6
        self.health = 100
        self.energy = 100
        self.xp = 0

        self.body = Entity(parent=self, model='cube', texture='white_cube', color=rgb(20,75,180), texture_scale=(2,2), scale=(1.2,1.5,0.6), position=(0,0.2,0))
        self.chest_plate = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(200,40,40), emissive_color=rgb(255,100,100), scale=(0.85,0.45,0.35), position=(0,0.1,0.57))
        self.left_shoulder = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(45,45,90), scale=(0.28,0.25,0.45), position=(-0.68,0.75,0))
        self.right_shoulder = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(45,45,90), scale=(0.28,0.25,0.45), position=(0.68,0.75,0))
        self.autobot_logo = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(255,40,40), emissive_color=rgb(255,90,90), scale=(0.18,0.18,0.05), position=(0,0.4,0.55))
        self.head = Entity(parent=self, model='cube', texture='white_cube', color=color.light_gray, texture_scale=(1,1), scale=(0.5,0.45,0.5), position=(0,1.25,0))
        self.visor = Entity(parent=self.head, model='cube', texture='white_cube', color=rgb(0,215,255), emissive_color=color.cyan, scale=(0.45,0.16,0.15), position=(0,0.03,0.53))
        self.ear_left = Entity(parent=self.head, model='cube', texture='white_cube', color=rgb(90,100,140), scale=(0.14,0.22,0.18), position=(-0.3,0,0))
        self.ear_right = Entity(parent=self.head, model='cube', texture='white_cube', color=rgb(90,100,140), scale=(0.14,0.22,0.18), position=(0.3,0,0))
        self.left_arm = Entity(parent=self, model='cube', texture='white_cube', color=rgb(180,180,210), texture_scale=(1,2), scale=(0.25,1.1,0.25), position=(-0.85,0.2,0))
        self.right_arm = Entity(parent=self, model='cube', texture='white_cube', color=rgb(180,180,210), texture_scale=(1,2), scale=(0.25,1.1,0.25), position=(0.85,0.2,0))
        self.left_leg = Entity(parent=self, model='cube', texture='white_cube', color=rgb(120,140,180), texture_scale=(1,2), scale=(0.35,1,0.35), position=(-0.3,-0.85,0))
        self.right_leg = Entity(parent=self, model='cube', texture='white_cube', color=rgb(120,140,180), texture_scale=(1,2), scale=(0.35,1,0.35), position=(0.3,-0.85,0))
        self.knee_left = Entity(parent=self.left_leg, model='cube', texture='white_cube', color=rgb(40,40,55), scale=(0.36,0.16,0.35), position=(0,-0.35,0.05), visible=False)
        self.knee_right = Entity(parent=self.right_leg, model='cube', texture='white_cube', color=rgb(40,40,55), scale=(0.36,0.16,0.35), position=(0,-0.35,0.05), visible=False)
        self.foot_left = Entity(parent=self.left_leg, model='cube', texture='white_cube', color=rgb(40,40,55), scale=(0.5,0.18,0.8), position=(0,-0.6,0.15), visible=False)
        self.foot_right = Entity(parent=self.right_leg, model='cube', texture='white_cube', color=rgb(40,40,55), scale=(0.5,0.18,0.8), position=(0,-0.6,0.15), visible=False)
        self.front = Entity(parent=self, model='cube', texture='white_cube', color=color.red, texture_scale=(2,1), scale=(1.3,0.4,1.4), position=(0,-0.1,1.3), visible=False)
        self.light_left = Entity(parent=self.front, model='cube', texture='white_cube', color=rgb(255,240,160), emissive_color=rgb(255,220,120), scale=(0.15,0.15,0.05), position=(-0.4,0.15,0.7), visible=False)
        self.light_right = Entity(parent=self.front, model='cube', texture='white_cube', color=rgb(255,240,160), emissive_color=rgb(255,220,120), scale=(0.15,0.15,0.05), position=(0.4,0.15,0.7), visible=False)
        self.wings = Entity(parent=self, model='cube', texture='white_cube', color=rgb(20,50,160), texture_scale=(3,1), scale=(3.5,0.1,1.5), position=(0,0.4,-1.5), visible=False)
        self.engine_left = Entity(parent=self, model='cube', texture='white_cube', color=rgb(90,90,110), scale=(0.3,0.2,0.3), position=(-1.2,0.1,-1.1), rotation=(90,0,0), visible=False)
        self.engine_right = Entity(parent=self, model='cube', texture='white_cube', color=rgb(90,90,110), scale=(0.3,0.2,0.3), position=(1.2,0.1,-1.1), rotation=(90,0,0), visible=False)
        self.tire_left = Entity(parent=self, model='cube', texture='white_cube', color=color.black, scale=(0.5,0.1,0.25), position=(-1.2,-0.45,0.5), rotation=(0,0,90), visible=False)
        self.tire_right = Entity(parent=self, model='cube', texture='white_cube', color=color.black, scale=(0.5,0.1,0.25), position=(1.2,-0.45,0.5), rotation=(0,0,90), visible=False)
        self.spoiler = Entity(parent=self, model='cube', texture='white_cube', color=rgb(70,70,90), scale=(1.4,0.1,0.3), position=(0,0.4,-1.2), visible=False)
        self.jet_nozzle_left = Entity(parent=self, model='cube', texture='white_cube', color=rgb(80,80,100), scale=(0.25,0.25,0.6), position=(-0.9,0.0,-1.9), visible=False)
        self.jet_nozzle_right = Entity(parent=self, model='cube', texture='white_cube', color=rgb(80,80,100), scale=(0.25,0.25,0.6), position=(0.9,0.0,-1.9), visible=False)

        self.set_mode_parts()

        self.transforming = False
        self.transform_time = 0.05
        self.transform_timer = 0
        self.transform_from = self.mode
        self.transform_to = self.mode
        self.transform_start_state = {}
        self.transform_end_state = {}
        self.transform_target_speed = self.speed

    def transform(self):
        if self.transforming:
            return

        if self.mode == "robot":
            target_mode = "vehicle"
            target_speed = 12
        elif self.mode == "vehicle":
            target_mode = "jet"
            target_speed = 18
        else:
            target_mode = "robot"
            target_speed = 6

        self.transforming = True
        self.transform_timer = 0
        self.transform_from = self.mode
        self.transform_to = target_mode
        self.transform_target_speed = target_speed
        self.transform_start_state = self.collect_current_state()
        self.transform_end_state = self.get_mode_state(target_mode)
        self.spawn_transform_effect()

    def spawn_transform_effect(self):
        if transform_sound:
            transform_sound.play()

        for i in range(5):
            shard = Entity(
                parent=self,
                model='quad',
                color=color.rgba(180,255,255,180),
                scale=(0.05,0.2),
                position=(0,0.2,0),
                rotation=(90, i * 72, 0),
                double_sided=True
            )
            target_scale = Vec3(3 + i * 0.6, 0.2, 1)
            shard.animate_scale(target_scale, duration=0.05, curve=curve.out_expo)
            shard.animate_color(color.rgba(180,255,255,0), duration=0.05)
            shard.animate_rotation((0, i * 72, 540), duration=0.05)
            destroy(shard, 0.08)

    def get_mode_state(self, mode):
        if mode == "robot":
            return {
                'body_scale': Vec3(1.2,1.5,0.6),
                'body_position': Vec3(0,0.2,0),
                'body_color': color.azure,
                'head_visible': True,
                'head_scale': Vec3(0.5,0.45,0.5),
                'head_position': Vec3(0,1.25,0),
                'left_arm_visible': True,
                'right_arm_visible': True,
                'left_arm_scale': Vec3(0.25,1.1,0.25),
                'right_arm_scale': Vec3(0.25,1.1,0.25),
                'left_arm_position': Vec3(-0.85,0.2,0),
                'right_arm_position': Vec3(0.85,0.2,0),
                'left_leg_visible': True,
                'right_leg_visible': True,
                'left_leg_position': Vec3(-0.3,-0.85,0),
                'right_leg_position': Vec3(0.3,-0.85,0),
                'front_visible': False,
                'front_scale': Vec3(1.3,0.4,1.4),
                'front_position': Vec3(0,-0.1,1.3),
                'wings_visible': False,
                'wings_position': Vec3(0,0.4,-1.5),
                'wings_scale': Vec3(3.5,0.1,1.5),
                'engine_visible': False,
                'engine_left_position': Vec3(-1.2,0.1,-1.1),
                'engine_right_position': Vec3(1.2,0.1,-1.1),
                'tire_visible': False,
                'tire_left_position': Vec3(-1.2,-0.45,0.5),
                'tire_right_position': Vec3(1.2,-0.45,0.5),
                'spoiler_visible': False,
                'spoiler_position': Vec3(0,0.35,-1.25),
                'jet_nozzle_visible': False,
                'jet_nozzle_left_position': Vec3(-0.9,0.0,-1.9),
                'jet_nozzle_right_position': Vec3(0.9,0.0,-1.9),
            }
        elif mode == "vehicle":
            return {
                'body_scale': Vec3(2,0.8,3.2),
                'body_position': Vec3(0,0.1,0),
                'body_color': color.red,
                'head_visible': False,
                'head_scale': Vec3(0.5,0.45,0.5),
                'head_position': Vec3(0,1.25,0),
                'left_arm_visible': True,
                'right_arm_visible': True,
                'left_arm_scale': Vec3(0.4,0.4,0.4),
                'right_arm_scale': Vec3(0.4,0.4,0.4),
                'left_arm_position': Vec3(-1.2,0.2,0.6),
                'right_arm_position': Vec3(1.2,0.2,0.6),
                'left_leg_visible': False,
                'right_leg_visible': False,
                'left_leg_position': Vec3(-0.3,-0.85,0),
                'right_leg_position': Vec3(0.3,-0.85,0),
                'front_visible': True,
                'front_scale': Vec3(2,0.4,1.2),
                'front_position': Vec3(0,-0.15,1.7),
                'wings_visible': False,
                'wings_position': Vec3(0,0.4,-1.5),
                'wings_scale': Vec3(3.5,0.1,1.5),
                'engine_visible': False,
                'engine_left_position': Vec3(-1.2,0.1,-1.1),
                'engine_right_position': Vec3(1.2,0.1,-1.1),
                'tire_visible': True,
                'tire_left_position': Vec3(-1.2,-0.45,0.9),
                'tire_right_position': Vec3(1.2,-0.45,0.9),
                'spoiler_visible': True,
                'spoiler_position': Vec3(0,0.35,-1.25),
                'jet_nozzle_visible': False,
                'jet_nozzle_left_position': Vec3(-0.9,0.0,-1.9),
                'jet_nozzle_right_position': Vec3(0.9,0.0,-1.9),
            }
        else:
            return {
                'body_scale': Vec3(3.5,0.6,4),
                'body_position': Vec3(0,0.1,-0.2),
                'body_color': color.orange,
                'head_visible': False,
                'head_scale': Vec3(0.5,0.45,0.5),
                'head_position': Vec3(0,1.25,0),
                'left_arm_visible': True,
                'right_arm_visible': True,
                'left_arm_scale': Vec3(0.4,0.4,0.4),
                'right_arm_scale': Vec3(0.4,0.4,0.4),
                'left_arm_position': Vec3(-1.5,0.2,0.6),
                'right_arm_position': Vec3(1.5,0.2,0.6),
                'left_leg_visible': False,
                'right_leg_visible': False,
                'left_leg_position': Vec3(-0.3,-0.85,0),
                'right_leg_position': Vec3(0.3,-0.85,0),
                'front_visible': True,
                'front_scale': Vec3(2.6,0.25,1.6),
                'front_position': Vec3(0,-0.15,1.1),
                'wings_visible': True,
                'wings_position': Vec3(0,0.35,-2.5),
                'wings_scale': Vec3(4,0.1,2.2),
                'engine_visible': True,
                'engine_left_position': Vec3(-1.3,0.1,-2.1),
                'engine_right_position': Vec3(1.3,0.1,-2.1),
                'tire_visible': False,
                'tire_left_position': Vec3(-1.2,-0.45,0.5),
                'tire_right_position': Vec3(1.2,-0.45,0.5),
                'spoiler_visible': False,
                'spoiler_position': Vec3(0,0.35,-1.25),
                'jet_nozzle_visible': True,
                'jet_nozzle_left_position': Vec3(-0.9,0.0,-1.9),
                'jet_nozzle_right_position': Vec3(0.9,0.0,-1.9),
            }

    def collect_current_state(self):
        return {
            'body_scale': self.body.scale,
            'body_position': self.body.position,
            'body_color': self.body.color,
            'head_visible': self.head.visible,
            'head_scale': self.head.scale,
            'head_position': self.head.position,
            'left_arm_visible': self.left_arm.visible,
            'right_arm_visible': self.right_arm.visible,
            'left_arm_scale': self.left_arm.scale,
            'right_arm_scale': self.right_arm.scale,
            'left_arm_position': self.left_arm.position,
            'right_arm_position': self.right_arm.position,
            'left_leg_visible': self.left_leg.visible,
            'right_leg_visible': self.right_leg.visible,
            'left_leg_position': self.left_leg.position,
            'right_leg_position': self.right_leg.position,
            'front_visible': self.front.visible,
            'front_scale': self.front.scale,
            'front_position': self.front.position,
            'wings_visible': self.wings.visible,
            'wings_position': self.wings.position,
            'wings_scale': self.wings.scale,
            'engine_visible': self.engine_left.visible,
            'engine_left_position': self.engine_left.position,
            'engine_right_position': self.engine_right.position,
            'tire_visible': self.tire_left.visible,
            'tire_left_position': self.tire_left.position,
            'tire_right_position': self.tire_right.position,
            'spoiler_visible': self.spoiler.visible,
            'spoiler_position': self.spoiler.position,
            'jet_nozzle_visible': self.jet_nozzle_left.visible,
            'jet_nozzle_left_position': self.jet_nozzle_left.position,
            'jet_nozzle_right_position': self.jet_nozzle_right.position,
        }

    def apply_transform_state(self, t):
        self.body.scale = lerp(self.transform_start_state['body_scale'], self.transform_end_state['body_scale'], t)
        self.body.position = lerp(self.transform_start_state['body_position'], self.transform_end_state['body_position'], t)
        self.body.color = lerp(self.transform_start_state['body_color'], self.transform_end_state['body_color'], t)
        self.head.scale = lerp(self.transform_start_state['head_scale'], self.transform_end_state['head_scale'], t)
        self.head.position = lerp(self.transform_start_state['head_position'], self.transform_end_state['head_position'], t)
        self.left_arm.scale = lerp(self.transform_start_state['left_arm_scale'], self.transform_end_state['left_arm_scale'], t)
        self.right_arm.scale = lerp(self.transform_start_state['right_arm_scale'], self.transform_end_state['right_arm_scale'], t)
        self.left_arm.position = lerp(self.transform_start_state['left_arm_position'], self.transform_end_state['left_arm_position'], t)
        self.right_arm.position = lerp(self.transform_start_state['right_arm_position'], self.transform_end_state['right_arm_position'], t)
        self.left_leg.position = lerp(self.transform_start_state['left_leg_position'], self.transform_end_state['left_leg_position'], t)
        self.right_leg.position = lerp(self.transform_start_state['right_leg_position'], self.transform_end_state['right_leg_position'], t)
        self.front.scale = lerp(self.transform_start_state['front_scale'], self.transform_end_state['front_scale'], t)
        self.front.position = lerp(self.transform_start_state['front_position'], self.transform_end_state['front_position'], t)
        self.wings.position = lerp(self.transform_start_state['wings_position'], self.transform_end_state['wings_position'], t)
        self.wings.scale = lerp(self.transform_start_state['wings_scale'], self.transform_end_state['wings_scale'], t)
        self.engine_left.position = lerp(self.transform_start_state['engine_left_position'], self.transform_end_state['engine_left_position'], t)
        self.engine_right.position = lerp(self.transform_start_state['engine_right_position'], self.transform_end_state['engine_right_position'], t)
        self.tire_left.position = lerp(self.transform_start_state['tire_left_position'], self.transform_end_state['tire_left_position'], t)
        self.tire_right.position = lerp(self.transform_start_state['tire_right_position'], self.transform_end_state['tire_right_position'], t)
        self.spoiler.position = lerp(self.transform_start_state['spoiler_position'], self.transform_end_state['spoiler_position'], t)
        self.jet_nozzle_left.position = lerp(self.transform_start_state['jet_nozzle_left_position'], self.transform_end_state['jet_nozzle_left_position'], t)
        self.jet_nozzle_right.position = lerp(self.transform_start_state['jet_nozzle_right_position'], self.transform_end_state['jet_nozzle_right_position'], t)

        self.head.visible = self.transform_end_state['head_visible'] if t >= 0.35 else self.transform_start_state['head_visible']
        self.front.visible = self.transform_end_state['front_visible'] if t >= 0.35 else self.transform_start_state['front_visible']
        self.wings.visible = self.transform_end_state['wings_visible'] if t >= 0.35 else self.transform_start_state['wings_visible']
        self.engine_left.visible = self.transform_end_state['engine_visible'] if t >= 0.35 else self.transform_start_state['engine_visible']
        self.engine_right.visible = self.transform_end_state['engine_visible'] if t >= 0.35 else self.transform_start_state['engine_visible']
        self.tire_left.visible = self.transform_end_state['tire_visible'] if t >= 0.35 else self.transform_start_state['tire_visible']
        self.tire_right.visible = self.transform_end_state['tire_visible'] if t >= 0.35 else self.transform_start_state['tire_visible']
        self.spoiler.visible = self.transform_end_state['spoiler_visible'] if t >= 0.35 else self.transform_start_state['spoiler_visible']
        self.jet_nozzle_left.visible = self.transform_end_state['jet_nozzle_visible'] if t >= 0.35 else self.transform_start_state['jet_nozzle_visible']
        self.jet_nozzle_right.visible = self.transform_end_state['jet_nozzle_visible'] if t >= 0.35 else self.transform_start_state['jet_nozzle_visible']

    def update(self):
        if self.transforming:
            self.transform_timer += time.dt
            t = min(self.transform_timer / self.transform_time, 1)
            self.apply_transform_state(t)

            if t >= 1:
                self.transforming = False
                self.mode = self.transform_to
                self.speed = self.transform_target_speed
                self.set_mode_parts()
        else:
            pass

    def set_mode_parts(self):
        if self.mode == "robot":
            self.body.scale = (1.2,1.5,0.6)
            self.body.position = (0,0.2,0)
            self.body.color = rgb(20,75,180)
            self.chest_plate.color = rgb(200,40,40)
            self.head.visible = True
            self.visor.visible = True
            self.left_shoulder.visible = True
            self.right_shoulder.visible = True
            self.autobot_logo.visible = True
            self.head.scale = (0.5,0.45,0.5)
            self.head.position = (0,1.25,0)
            self.left_arm.visible = True
            self.right_arm.visible = True
            self.left_arm.color = rgb(180,180,210)
            self.right_arm.color = rgb(180,180,210)
            self.left_arm.scale = (0.25,1.1,0.25)
            self.right_arm.scale = (0.25,1.1,0.25)
            self.left_arm.position = (-0.85,0.2,0)
            self.right_arm.position = (0.85,0.2,0)
            self.left_leg.visible = True
            self.right_leg.visible = True
            self.knee_left.visible = True
            self.knee_right.visible = True
            self.foot_left.visible = True
            self.foot_right.visible = True
            self.left_leg.position = (-0.3,-0.85,0)
            self.right_leg.position = (0.3,-0.85,0)
            self.front.visible = False
            self.light_left.visible = False
            self.light_right.visible = False
            self.wings.visible = False
            self.engine_left.visible = False
            self.engine_right.visible = False
            self.tire_left.visible = False
            self.tire_right.visible = False
            self.spoiler.visible = False
            self.jet_nozzle_left.visible = False
            self.jet_nozzle_right.visible = False
        elif self.mode == "vehicle":
            self.body.scale = (2,0.8,3.2)
            self.body.position = (0,0.1,0)
            self.body.color = color.red
            self.chest_plate.color = rgb(200,40,40)
            self.head.visible = False
            self.visor.visible = False
            self.left_shoulder.visible = False
            self.right_shoulder.visible = False
            self.autobot_logo.visible = True
            self.left_arm.visible = True
            self.right_arm.visible = True
            self.left_arm.color = rgb(170,170,190)
            self.right_arm.color = rgb(170,170,190)
            self.left_arm.scale = (0.4,0.4,0.4)
            self.right_arm.scale = (0.4,0.4,0.4)
            self.left_arm.position = (-1.2,0.2,0.6)
            self.right_arm.position = (1.2,0.2,0.6)
            self.left_leg.visible = False
            self.right_leg.visible = False
            self.knee_left.visible = False
            self.knee_right.visible = False
            self.foot_left.visible = False
            self.foot_right.visible = False
            self.front.visible = True
            self.front.scale = (2,0.4,1.2)
            self.front.position = (0,-0.15,1.7)
            self.light_left.visible = True
            self.light_right.visible = True
            self.wings.visible = False
            self.engine_left.visible = False
            self.engine_right.visible = False
            self.tire_left.visible = True
            self.tire_right.visible = True
            self.tire_left.position = (-1.2,-0.45,0.9)
            self.tire_right.position = (1.2,-0.45,0.9)
            self.spoiler.visible = True
            self.jet_nozzle_left.visible = False
            self.jet_nozzle_right.visible = False
        else:
            self.body.scale = (3.5,0.6,4)
            self.body.position = (0,0.1,-0.2)
            self.body.color = rgb(40,40,60)
            self.chest_plate.color = rgb(80,20,130)
            self.head.visible = False
            self.visor.visible = False
            self.left_shoulder.visible = False
            self.right_shoulder.visible = False
            self.autobot_logo.visible = False
            self.left_arm.visible = True
            self.right_arm.visible = True
            self.left_arm.color = rgb(170,170,190)
            self.right_arm.color = rgb(170,170,190)
            self.left_arm.scale = (0.4,0.4,0.4)
            self.right_arm.scale = (0.4,0.4,0.4)
            self.left_arm.position = (-1.5,0.2,0.6)
            self.right_arm.position = (1.5,0.2,0.6)
            self.left_leg.visible = False
            self.right_leg.visible = False
            self.knee_left.visible = False
            self.knee_right.visible = False
            self.foot_left.visible = False
            self.foot_right.visible = False
            self.front.visible = True
            self.front.scale = (2.6,0.25,1.6)
            self.front.position = (0,-0.15,1.1)
            self.light_left.visible = True
            self.light_right.visible = True
            self.wings.visible = True
            self.wings.position = (0,0.35,-2.5)
            self.wings.scale = (4,0.1,2.2)
            self.engine_left.visible = True
            self.engine_right.visible = True
            self.engine_left.position = (-1.3,0.1,-2.1)
            self.engine_right.position = (1.3,0.1,-2.1)
            self.tire_left.visible = False
            self.tire_right.visible = False
            self.spoiler.visible = False
            self.jet_nozzle_left.visible = True
            self.jet_nozzle_right.visible = True

    def fire(self):
        if self.transforming or self.energy < 5:
            return

        self.energy -= 5
        bullet_color = color.yellow
        bullet_speed = 30
        bullet_damage = 20

        if self.mode == "vehicle":
            bullet_color = color.red
            bullet_speed = 35
            bullet_damage = 18

        if self.mode == "jet":
            bullet_color = color.cyan
            bullet_speed = 45
            bullet_damage = 25

        Bullet(
            self.world_position + self.forward * 1.5 + Vec3(0,1,0),
            self.forward,
            color=bullet_color,
            speed=bullet_speed,
            damage=bullet_damage
        )

    def update(self):
        if self.transforming:
            self.rotation_y += 120 * time.dt


class Enemy(Entity):
    def __init__(self, pos):
        super().__init__(
            model='cube',
            color=color.rgba(0,0,0,0),
            position=pos,
            scale=1
        )

        self.health = 40
        self.body = Entity(parent=self, model='cube', texture='white_cube', color=rgb(90,0,140), emissive_color=rgb(65,0,90), texture_scale=(2,2), scale=(1.2,1.4,0.8), position=(0,0.2,0))
        self.chest = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(30,0,60), emissive_color=rgb(40,0,80), texture_scale=(1,1), scale=(0.95,0.9,0.5), position=(0,0.6,0.15))
        self.head = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(140,0,190), emissive_color=rgb(130,0,190), texture_scale=(1,1), scale=(0.45,0.35,0.45), position=(0,1.1,0))
        self.eye_left = Entity(parent=self.head, model='cube', texture='white_cube', color=color.red, emissive_color=color.red, scale=(0.1,0.08,0.05), position=(-0.15,0.05,0.26))
        self.eye_right = Entity(parent=self.head, model='cube', texture='white_cube', color=color.red, emissive_color=color.red, scale=(0.1,0.08,0.05), position=(0.15,0.05,0.26))
        self.left_horn = Entity(parent=self.head, model='cube', texture='white_cube', color=rgb(70,0,90), scale=(0.12,0.22,0.12), position=(-0.23,0.12,0))
        self.right_horn = Entity(parent=self.head, model='cube', texture='white_cube', color=rgb(70,0,90), scale=(0.12,0.22,0.12), position=(0.23,0.12,0))
        self.left_arm = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(140,0,140), emissive_color=rgb(120,0,120), texture_scale=(1,2), scale=(0.28,0.9,0.28), position=(-0.9,0.2,0))
        self.right_arm = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(140,0,140), emissive_color=rgb(120,0,120), texture_scale=(1,2), scale=(0.28,0.9,0.28), position=(0.9,0.2,0))
        self.left_gun = Entity(parent=self.left_arm, model='cube', texture='white_cube', color=color.gray, emissive_color=rgb(150,150,150), texture_scale=(1,1), scale=(0.22,0.22,0.9), position=(0,-0.2,0.55))
        self.right_gun = Entity(parent=self.right_arm, model='cube', texture='white_cube', color=color.gray, emissive_color=rgb(150,150,150), texture_scale=(1,1), scale=(0.22,0.22,0.9), position=(0,-0.2,0.55))
        self.left_leg = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(90,0,120), emissive_color=rgb(60,0,90), texture_scale=(1,2), scale=(0.4,1.05,0.4), position=(-0.35,-1.0,0))
        self.right_leg = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(90,0,120), emissive_color=rgb(60,0,90), texture_scale=(1,2), scale=(0.4,1.05,0.4), position=(0.35,-1.0,0))

    def update(self):
        self.look_at(player)

        if distance(self, player) > 2:
            self.position += self.forward * 3 * time.dt

        if distance(self, player) < 1.5:
            player.health -= 10 * time.dt


class Boss(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.rgba(0,0,0,0),
            scale=1,
            position=(0,2,35)
        )

        self.health = 300
        self.last_shot = 0
        self.body = Entity(parent=self, model='cube', texture='white_cube', color=rgb(80,0,120), emissive_color=rgb(45,0,80), texture_scale=(3,3), scale=(3.6,3.5,2.6), position=(0,0.7,0))
        self.shoulder_left = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(65,0,100), emissive_color=rgb(85,0,120), scale=(1.2,0.35,1.2), position=(-2.05,1.0,0))
        self.shoulder_right = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(65,0,100), emissive_color=rgb(85,0,120), scale=(1.2,0.35,1.2), position=(2.05,1.0,0))
        self.chest = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(55,0,95), emissive_color=rgb(40,0,75), texture_scale=(2,2), scale=(2.4,2.0,1.2), position=(0,1.3,0.8))
        self.logo_plate = Entity(parent=self.chest, model='cube', texture='white_cube', color=color.black, emissive_color=rgb(30,0,30), scale=(1.8,0.35,0.15), position=(0,0.35,0.58))
        self.decepticon_emblem = Entity(parent=self.logo_plate, model='cube', texture='white_cube', color=rgb(190,50,190), emissive_color=rgb(220,100,220), scale=(0.5,0.5,0.08), position=(0,0.05,0.08))
        self.head = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(150,0,190), emissive_color=rgb(120,0,180), texture_scale=(1,1), scale=(1.0,0.85,1.0), position=(0,2.4,0))
        self.eye_left = Entity(parent=self.head, model='cube', texture='white_cube', color=color.red, emissive_color=color.red, scale=(0.16,0.1,0.06), position=(-0.2,0.05,0.52))
        self.eye_right = Entity(parent=self.head, model='cube', texture='white_cube', color=color.red, emissive_color=color.red, scale=(0.16,0.1,0.06), position=(0.2,0.05,0.52))
        self.head_spike_left = Entity(parent=self.head, model='cube', texture='white_cube', color=rgb(90,0,90), scale=(0.18,0.28,0.18), position=(-0.35,0.14,0))
        self.head_spike_right = Entity(parent=self.head, model='cube', texture='white_cube', color=rgb(90,0,90), scale=(0.18,0.28,0.18), position=(0.35,0.14,0))
        self.left_arm = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(100,100,110), emissive_color=rgb(130,130,140), texture_scale=(1,2), scale=(0.5,1.8,0.5), position=(-1.6,0.8,0))
        self.right_arm = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(100,100,110), emissive_color=rgb(130,130,140), texture_scale=(1,2), scale=(0.5,1.8,0.5), position=(1.6,0.8,0))
        self.left_cannon = Entity(parent=self.left_arm, model='cube', texture='white_cube', color=rgb(160,160,160), emissive_color=rgb(220,220,220), texture_scale=(1,1), scale=(0.4,0.4,1.6), position=(0,-0.2,0.8), rotation=(90,0,0))
        self.right_cannon = Entity(parent=self.right_arm, model='cube', texture='white_cube', color=rgb(160,160,160), emissive_color=rgb(220,220,220), texture_scale=(1,1), scale=(0.4,0.4,1.6), position=(0,-0.2,0.8), rotation=(90,0,0))
        self.left_leg = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(65,0,100), emissive_color=rgb(40,0,70), texture_scale=(1,2), scale=(0.85,2.2,0.85), position=(-0.8,-1.4,0))
        self.right_leg = Entity(parent=self.body, model='cube', texture='white_cube', color=rgb(65,0,100), emissive_color=rgb(40,0,70), texture_scale=(1,2), scale=(0.85,2.2,0.85), position=(0.8,-1.4,0))
        self.visor = Entity(parent=self.head, model='cube', texture='white_cube', color=color.cyan, emissive_color=color.cyan, scale=(0.55,0.22,0.1), position=(0,0.08,0.51))
        self.nameplate = Text(text='MEGATRON', parent=self, position=(0,3.5,0), origin=(0,0), color=color.magenta, scale=2, world_scale=1)

    def fire(self):
        target = (player.world_position - self.world_position).normalized()
        EnemyBullet(self.left_cannon.world_position + target * 0.5, target)
        EnemyBullet(self.right_cannon.world_position + target * 0.5, target)
        if boss_fire_sound:
            boss_fire_sound.play()

    def update(self):
        self.look_at(player)

        if distance(self, player) > 5:
            self.position += self.forward * 2 * time.dt

        if time.time() - self.last_shot > 1.5:
            self.fire()
            self.last_shot = time.time()

        if distance(self, player) < 4:
            player.health -= 20 * time.dt


class EnergyCube(Entity):
    def __init__(self, pos):
        super().__init__(
            model='cube',
            color=color.cyan,
            scale=.8,
            position=pos
        )

# ---------- WORLD ----------

ground = Entity(
    model='plane',
    scale=80,
    texture='white_cube',
    texture_scale=(40,40),
    color=rgb(35,35,55),
    emissive_color=rgb(10,10,20)
)

Sky()

player = Player()

camera.parent = player
camera.position = (0,8,-18)
camera.rotation_x = 20

ui_panel = Entity(
    parent=camera.ui,
    model='quad',
    texture='white_cube',
    texture_scale=(8,8),
    color=color.rgba(0,0,0,150),
    scale=(0.38,0.22),
    position=(-0.7,0.15,0)
)

# ---------- GAME OBJECTS ----------

enemies = []
cubes = []

for i in range(12):
    enemies.append(
        Enemy(
            (
                uniform(-25,25),
                1,
                uniform(-25,25)
            )
        )
    )

for i in range(10):
    cubes.append(
        EnergyCube(
            (
                uniform(-30,30),
                1,
                uniform(-30,30)
            )
        )
    )

boss = None

# ---------- UI ----------

health_text = Text(text='', position=(-0.85,0.45), color=color.lime, scale=1.1)
energy_text = Text(text='', position=(-0.85,0.40), color=color.cyan, scale=1.1)
mode_text = Text(text='', position=(-0.85,0.35), color=color.azure, scale=1.1)
status_text = Text(text='READY', position=(-0.85,0.30), color=color.orange, scale=0.9)
mission_text = Text(text='Mission: Defeat 12 Decepticons', position=(-0.85,0.25), color=color.magenta, scale=1.0)
action_text = Text(text='T: Transform  SPACE: Fire  Q: Missile  SHIFT: Boost', position=(-0.85,0.18), color=color.white, scale=0.7)

# ---------- INPUT ----------

def input(key):
    if key == 't':
        player.transform()

    if key == 'space':
        player.fire()

    if key == 'q' and player.energy >= 25:
        player.energy -= 25
        Missile(
            player.world_position + player.forward * 2 + Vec3(0,1,0),
            player.forward
        )

# ---------- UPDATE ----------

def update():

    speed = player.speed

    if held_keys['shift'] and player.mode in ('vehicle', 'jet') and player.energy > 0:
        speed *= 2
        player.energy = max(0, player.energy - 30 * time.dt)

    player.x += (held_keys['d'] - held_keys['a']) * speed * time.dt
    player.z += (held_keys['w'] - held_keys['s']) * speed * time.dt

    if not (held_keys['shift'] and player.mode in ('vehicle', 'jet')):
        player.energy = min(100, player.energy + 10 * time.dt)

    for cube in cubes[:]:
        if distance(player, cube) < 1.5:
            player.energy = min(
                100,
                player.energy + 25
            )

            destroy(cube)
            cubes.remove(cube)

    global boss

    if player.xp >= 120 and boss is None:
        boss = Boss()
        mission_text.text = 'Mission: Defeat Megatron!'

    if boss:
        if distance(player, boss) < 2 and held_keys['space']:
            boss.health -= 20 * time.dt

        if boss.health <= 0:
            Text(
                'YOU WIN!',
                scale=3,
                origin=(0,0)
            )
            application.pause()

    if player.health <= 0:
        Text(
            'GAME OVER',
            scale=3,
            origin=(0,0)
        )
        application.pause()

    health_text.text = f'Health: {int(player.health)}'
    energy_text.text = f'Power Core: {int(player.energy)}'
    mode_text.text = f'Mode: {player.mode.title()}'
    status_text.text = 'TRANSFORMING...' if player.transforming else f'{player.mode.upper()} READY'
app.run()