from ursina import *
from ursina import Cylinder
from random import uniform, choice, randint
import math
import time

app = Ursina()

# ==========================
# WINDOW SETTINGS
# ==========================
window.title = "Transformers: Cyber Battle"
window.borderless = False
window.fullscreen = False
window.size = (1280, 720)

# ==========================
# GAME STATE – start directly in 'playing'
# ==========================
game_state = 'playing'          # 'menu' or 'playing' – now starts playing

# ==========================
# DAY/NIGHT CYCLE
# ==========================
time_of_day = 0.0
cycle_speed = 0.001

def update_day_night():
    global time_of_day
    time_of_day += cycle_speed
    if time_of_day > 1.0:
        time_of_day -= 1.0

    sun_angle = math.sin(time_of_day * 2 * math.pi)
    sun_angle = max(-0.2, min(1.0, sun_angle))

    sun_y = 50 * sun_angle
    sun_x = 50 * math.cos(time_of_day * 2 * math.pi)
    sun_z = 50 * math.sin(time_of_day * 2 * math.pi)
    for light in scene.entities:
        if isinstance(light, DirectionalLight):
            light.look_at(Vec3(sun_x, sun_y, sun_z))

    day_color = color.rgb(135/255, 206/255, 235/255)
    night_color = color.rgb(20/255, 30/255, 60/255)
    dusk_color = color.rgb(200/255, 100/255, 50/255)
    brightness = max(0.0, min(1.0, (sun_angle + 0.2) / 1.2))
    sky_color = lerp(night_color, day_color, brightness)
    if abs(sun_angle) < 0.15:
        sky_color = lerp(sky_color, dusk_color, 0.5)
    Sky(color=sky_color)
    scene.fog_color = sky_color
    scene.fog_density = 0.02 - 0.01 * brightness
    ambient = brightness * 0.5 + 0.2
    scene.ambient_color = Color(ambient, ambient, ambient, 1)

# ==========================
# ATMOSPHERE & LIGHTING
# ==========================
scene.fog_color = color.rgb(150/255, 190/255, 255/255)
scene.fog_density = 0.025
dir_light = DirectionalLight(shadow_map_resolution=(1024, 1024), shadows=False)
Sky(color=color.rgb(135/255, 206/255, 235/255))

# ==========================
# INFINITE GROUND
# ==========================
ground = Entity(
    model='plane',
    scale=2000,
    texture='grass',
    texture_scale=(400, 400),
    color=color.white,
    collider=None
)

# ==========================
# HELPER FOR CYLINDERS
# ==========================
def make_cylinder(radius, height, color, pos, rot=(0,0,0), parent=None):
    return Entity(
        model=Cylinder(resolution=8, radius=radius, height=height),
        color=color,
        position=pos,
        rotation=rot,
        parent=parent
    )

# ==========================
# CLOUDS
# ==========================
def create_cloud(position, scale=5):
    cloud = Entity(
        model='sphere',
        color=Color(1, 1, 1, 0.7),
        scale=scale,
        position=position,
        rotation=Vec3(uniform(0,360), uniform(0,360), uniform(0,360))
    )
    for _ in range(2):
        offset = Vec3(uniform(-scale*0.4, scale*0.4), uniform(-scale*0.2, scale*0.2), uniform(-scale*0.4, scale*0.4))
        Entity(model='sphere', color=Color(1,1,1,0.5), scale=scale*uniform(0.4,0.6), parent=cloud, position=offset)

for i in range(8):
    create_cloud(Vec3(uniform(-100,100), uniform(20,40), uniform(-100,100)), uniform(3,8))

# ==========================
# BUILDINGS
# ==========================
building_colors = [
    color.rgb(200/255, 200/255, 210/255),
    color.rgb(160/255, 160/255, 170/255),
    color.rgb(120/255, 120/255, 130/255),
    color.rgb(180/255, 140/255, 100/255),
    color.rgb(210/255, 180/255, 140/255),
    color.rgb(100/255, 150/255, 200/255),
]

buildings = []
for i in range(40):
    w = uniform(2, 5)
    h = uniform(5, 15)
    d = uniform(2, 5)
    b = Entity(
        model='cube',
        color=choice(building_colors),
        scale=(w, h, d),
        position=(uniform(-70,70), h/2, uniform(-70,70)),
        collider='box'
    )
    buildings.append(b)

# ==========================
# TREES
# ==========================
tree_entities = []

def create_tree(x, z):
    trunk_h = uniform(1.5, 3)
    trunk = Entity(
        model='cube',
        color=color.rgb(101/255,67/255,33/255),
        scale=(0.3, trunk_h, 0.3),
        position=(x, trunk_h/2, z),
        collider='box'
    )
    crown_size = uniform(1.5, 3)
    crown = Entity(
        model='sphere',
        color=color.rgb(34/255,139/255,34/255),
        scale=crown_size,
        position=(x, trunk_h + crown_size*0.7, z),
        collider='sphere'
    )
    trunk.health = 3
    crown.health = 3
    trunk.parent_entity = crown
    crown.parent_entity = trunk
    tree_entities.append(trunk)
    tree_entities.append(crown)
    return trunk, crown

trees = []
for i in range(50):
    x, z = uniform(-75,75), uniform(-75,75)
    t, c = create_tree(x, z)
    trees.append((t, c))

# ==========================
# ROCKS
# ==========================
rock_entities = []

def create_rock(x, z):
    size = uniform(0.5, 1.0)
    r = Entity(
        model='sphere',
        color=color.rgb(150/255,150/255,150/255),
        scale=(size, size*uniform(0.5,0.8), size),
        position=(x, size*0.4, z),
        rotation=Vec3(uniform(0,360), uniform(0,360), uniform(0,360)),
        collider='sphere'
    )
    r.health = 5
    rock_entities.append(r)
    return r

rocks = []
for i in range(15):
    x, z = uniform(-70,70), uniform(-70,70)
    r = create_rock(x, z)
    rocks.append(r)

# ==========================
# OBSTACLES
# ==========================
def update_obstacles():
    global obstacles
    obstacles = buildings + tree_entities + rock_entities

update_obstacles()

# ==========================
# COLLISION
# ==========================
def move_entity_with_collision(entity, movement, obstacles):
    if movement.length() == 0:
        return
    new_pos = entity.position + movement
    entity.position = new_pos
    if any(entity.intersects(obs).hit for obs in obstacles):
        entity.position -= movement
        move_x = Vec3(movement.x, 0, 0)
        entity.position += move_x
        if any(entity.intersects(obs).hit for obs in obstacles):
            entity.position -= move_x
        move_z = Vec3(0, 0, movement.z)
        entity.position += move_z
        if any(entity.intersects(obs).hit for obs in obstacles):
            entity.position -= move_z

# ==========================
# EFFECTS
# ==========================
def explosion(position, c=color.orange, size=2.0):
    try:
        b = Entity(model='sphere', color=c, scale=.5, position=position)
        b.animate_scale(size, duration=.25)
        b.animate_color(Color(0,0,0,0), duration=.25)
        destroy(b, delay=.3)
    except:
        pass

def particle_burst(position, count=15, color=color.yellow, speed=2):
    try:
        for _ in range(count):
            p = Entity(model='sphere', color=color, scale=uniform(0.05, 0.15), position=position)
            dx, dy, dz = uniform(-1,1), uniform(0.5,2), uniform(-1,1)
            if abs(dx) < 0.01 and abs(dy) < 0.01 and abs(dz) < 0.01:
                dx, dy, dz = 1, 1, 1
            dir = Vec3(dx, dy, dz).normalized() * uniform(1, speed)
            p.animate_position(p.position + dir, duration=uniform(0.3,0.6), curve=curve.out_quad)
            p.animate_scale(0, duration=uniform(0.3,0.6))
            p.animate_color(Color(0,0,0,0), duration=uniform(0.3,0.6))
            destroy(p, delay=0.6)
    except:
        pass

def muzzle_flash(position):
    try:
        for sc, dur in [(.3,.1),(.5,.15)]:
            f = Entity(model='sphere', color=color.yellow, scale=sc, position=position)
            f.animate_scale(sc*4, duration=dur)
            f.animate_color(Color(0,0,0,0), duration=dur)
            destroy(f, delay=dur)
    except:
        pass

# ==========================
# RESOURCE PICKUPS
# ==========================
resource_pickups = []

class ResourcePickup(Entity):
    def __init__(self, position, resource_type):
        self.resource_type = resource_type
        color_map = {'wood': color.rgb(139/255,69/255,19/255), 'stone': color.rgb(160/255,160/255,160/255)}
        super().__init__(
            model='cube',
            color=color_map.get(resource_type, color.white),
            scale=0.3,
            position=position + Vec3(0, 0.3, 0),
            collider='box'
        )
        self.rotation_y = 0
        self.bob_offset = 0
        resource_pickups.append(self)

    def update(self):
        self.rotation_y += 100 * time.dt
        self.bob_offset += time.dt
        self.y = self.position.y + math.sin(self.bob_offset * 3) * 0.05

# ==========================
# INVENTORY
# ==========================
inventory = {'wood': 0, 'stone': 0}

def collect_resource(pickup):
    global inventory
    inventory[pickup.resource_type] += 1
    if mission.type == 'gather' and not mission.completed:
        if mission.resource_type == pickup.resource_type:
            mission.progress += 1
            if mission.progress >= mission.target:
                mission.complete()
    particle_burst(pickup.position, count=8, color=color.green)
    destroy(pickup)
    if pickup in resource_pickups:
        resource_pickups.remove(pickup)

def collect_health_pack(pack):
    player.health = min(player.max_health, player.health + 25)
    if mission.type == 'collect_health' and not mission.completed:
        mission.progress += 1
        if mission.progress >= mission.target:
            mission.complete()
    particle_burst(pack.position, count=10, color=color.green)
    destroy(pack)
    global health_packs
    if pack in health_packs:
        health_packs.remove(pack)

# ==========================
# MISSION SYSTEM
# ==========================
class Mission:
    def __init__(self):
        self.level = 1
        self.type = None
        self.target = 0
        self.progress = 0
        self.completed = False
        self.description = ""
        self.resource_type = None
        self.generate_new()

    def generate_new(self):
        self.type = choice(['kill', 'collect_health', 'gather', 'survive'])
        if self.type == 'kill':
            self.target = 5 + self.level * 5
            self.description = f"Kill {self.target} enemies"
        elif self.type == 'collect_health':
            self.target = 2 + self.level * 2
            self.description = f"Collect {self.target} health packs"
        elif self.type == 'gather':
            self.resource_type = choice(['wood', 'stone'])
            self.target = 3 + self.level * 2
            self.description = f"Gather {self.target} {self.resource_type}"
        else:
            self.target = 15 + self.level * 5
            self.description = f"Survive {self.target} seconds"
        self.progress = 0
        self.completed = False
        self.start_time = time.time()

    def update(self, player, enemies, health_packs):
        if self.completed:
            return
        if self.type == 'survive':
            self.progress = int(time.time() - self.start_time)
            if self.progress >= self.target:
                self.complete()

    def complete(self):
        global score
        self.completed = True
        bonus = 50 + self.level * 10
        score += bonus
        explosion(player.position, c=GOLD, size=3)
        particle_burst(player.position, count=25, color=GOLD, speed=4)
        self.level += 1
        self.generate_new()
        mission_complete_text.text = f"Mission Complete! +{bonus} score"
        mission_complete_text.enabled = True
        invoke(setattr, mission_complete_text, 'enabled', False, delay=2)

    def get_progress_text(self):
        if self.type == 'survive':
            return f"{self.progress}/{self.target}s"
        else:
            return f"{self.progress}/{self.target}"

# ==========================
# GLOBALS
# ==========================
enemies   = []
health_packs = []
score     = 0
combo     = 0
max_combo = 0
game_over = False
megatron_defeated = False
spawn_timer = 0
health_pack_timer = 0

mission = Mission()

# ==========================
# COLOURS
# ==========================
RED    = color.rgb(190/255,  18/255,  18/255)
BLUE   = color.rgb( 10/255,  25/255, 120/255)
SILVER = color.rgb(192/255, 192/255, 192/255)
BLACK  = color.rgb( 15/255,  15/255,  20/255)
CYAN   = color.rgb(100/255, 210/255, 255/255)
CHROME = color.rgb(140/255, 148/255, 158/255)
YELLOW = color.rgb(255/255, 190/255,   0/255)
GOLD   = color.rgb(255/255, 215/255, 0/255)

# Megatron colours
MEGATRON_GRAY = color.rgb(100/255, 100/255, 110/255)
MEGATRON_PURPLE = color.rgb(130/255, 0/255, 200/255)
MEGATRON_RED = color.rgb(220/255, 20/255, 20/255)
MEGATRON_DARK = color.rgb(50/255, 50/255, 60/255)

# ==========================
# PLAYER
# ==========================
class Player(Entity):
    def __init__(self):
        super().__init__(position=(0,1,0), collider='box')
        self.health         = 1000000
        self.max_health     = 1000000
        self.speed          = 8
        self.jump_speed     = 8
        self.vertical_speed = 0
        self.gravity        = 20
        self.shoot_cooldown = 0
        self.melee_cooldown = 0
        self.dash_cooldown  = 0
        self.matrix_cooldown = 0
        self.shield_active = False
        self.dashing = False
        self.dash_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.matrix_boost = False
        self.matrix_boost_timer = 0
        self.original_speed = 8

        self.mode = 'robot'
        self.truck_speed = 15
        self.target_rotation_y = 0

        # ---------- ROBOT ----------
        r = Entity(parent=self)
        self.robot = r
        def p(model, col, scale, pos):
            return Entity(model=model, color=col, scale=scale, position=pos, parent=r)
        p('cube', BLACK,  (.42,.14,.56), (-.35,-.33,.08))
        p('cube', BLACK,  (.42,.14,.56), ( .35,-.33,.08))
        self.left_shin  = p('cube', RED, (.36,.52,.38), (-.35,-.04,0))
        self.right_shin = p('cube', RED, (.36,.52,.38), ( .35,-.04,0))
        self.left_thigh  = p('cube', BLUE, (.4,.55,.4), (-.35,.48,0))
        self.right_thigh = p('cube', BLUE, (.4,.55,.4), ( .35,.48,0))
        p('cube', BLACK, (.92,.22,.52), (0,.84,0))
        torso = Entity(model='cube', color=RED, scale=(1.42,1.18,.76), position=(0,1.68,0), parent=r)
        self.body = torso
        Entity(model='cube', color=BLUE,   scale=(.36,.62,.13), position=(-.3,.04,.45),  parent=torso)
        Entity(model='cube', color=BLUE,   scale=(.36,.62,.13), position=( .3,.04,.45),  parent=torso)
        self.matrix_glow = Entity(model='cube', color=CYAN, scale=(.20,.20,.09), position=(0,.13,.48), parent=torso)
        Entity(model='cube', color=SILVER, scale=(.30,.30,.07), position=(0,.13,.46), parent=torso)
        Entity(model='cube', color=BLACK,  scale=(.80,.10,.08), position=(0,-.38,.46), parent=torso)
        p('cube', CHROME, (.13,.72,.13), (-.84,2.08,-.12))
        p('cube', CHROME, (.13,.72,.13), ( .84,2.08,-.12))
        p('cube', BLUE, (.36,.24,.62), (-1.02,2.14,0))
        p('cube', BLUE, (.36,.24,.62), ( 1.02,2.14,0))
        self.left_arm  = p('cube', BLUE, (.32,.62,.32), (-1.02,1.68,0))
        self.right_arm = p('cube', BLUE, (.32,.62,.32), ( 1.02,1.68,0))
        self.left_forearm  = p('cube', RED, (.28,.52,.28), (-1.02,1.10,0))
        self.right_forearm = p('cube', RED, (.28,.52,.28), ( 1.02,1.10,0))
        p('cube', SILVER, (.26,.22,.26), (-1.02,.76,0))
        p('cube', SILVER, (.26,.22,.26), ( 1.02,.76,0))
        p('cube', BLACK, (.16,.32,.16), (1.02,.54,0))
        p('cube', BLACK, (.30,.22,.28), (0,2.38,0))
        head = Entity(model='cube', color=BLUE, scale=(.64,.56,.54), position=(0,2.74,0), parent=r)
        self.head = head
        Entity(model='cube', color=SILVER, scale=(.78,.34,.12), position=(0,-.18,.48), parent=head)
        Entity(model='cube', color=CYAN,   scale=(.58,.17,.09), position=(0,.10,.50),  parent=head)
        Entity(model='cube', color=RED,    scale=(.17,.30,.10), position=(0,.42,.10),  parent=head)
        Entity(model='cube', color=BLUE,   scale=(.14,.44,.32), position=(-.52,.07,0), parent=head)
        Entity(model='cube', color=BLUE,   scale=(.14,.44,.32), position=( .52,.07,0), parent=head)
        Entity(model='cube', color=SILVER, scale=(.07,.20,.07), position=(-.36,.54,0), parent=head)
        Entity(model='cube', color=SILVER, scale=(.07,.20,.07), position=( .36,.54,0), parent=head)

        # Energon Axe
        self.axe = Entity(
            model='cube',
            color=color.cyan,
            scale=(0.15, 0.9, 0.4),
            position=(0.5, 0.1, 0),
            parent=self.right_arm,
            enabled=False
        )

        # ---------- TRUCK (realistic) ----------
        self.truck = Entity(parent=self, enabled=False)
        def add_part(model, col, scale, pos, rot=(0,0,0)):
            return Entity(model=model, color=col, scale=scale, position=pos, rotation=rot, parent=self.truck)

        # Cab
        add_part('cube', RED, (1.6, 1.2, 1.8), (0, 0.6, 0))
        add_part('cube', color.rgb(220/255, 40/255, 40/255), (1.5, 0.3, 1.7), (0, 1.3, 0))
        add_part('cube', color.azure, (1.0, 0.5, 0.1), (0, 0.8, 0.95))
        add_part('cube', color.azure, (0.1, 0.3, 0.6), (-0.75, 0.7, 0.5))
        add_part('cube', color.azure, (0.1, 0.3, 0.6), ( 0.75, 0.7, 0.5))
        add_part('cube', BLACK, (0.8, 0.4, 0.05), (0, 0.3, 0.95))
        for x in [-0.3, 0, 0.3]:
            add_part('cube', SILVER, (0.05, 0.3, 0.06), (x, 0.3, 0.98))
        add_part('cube', SILVER, (1.4, 0.2, 0.3), (0, 0.1, 0.95))
        add_part('sphere', YELLOW, 0.15, (-0.5, 0.3, 0.95))
        add_part('sphere', YELLOW, 0.15, ( 0.5, 0.3, 0.95))
        make_cylinder(0.06, 0.9, CHROME, (-0.6, 0.9, -0.4), rot=(0,0,0), parent=self.truck)
        make_cylinder(0.06, 0.9, CHROME, ( 0.6, 0.9, -0.4), rot=(0,0,0), parent=self.truck)
        add_part('cube', SILVER, (0.08, 0.08, 0.08), (-0.9, 1.0, 0.4))
        add_part('cube', SILVER, (0.08, 0.08, 0.08), ( 0.9, 1.0, 0.4))

        # Trailer
        add_part('cube', BLUE, (2.8, 1.6, 4.0), (0, 0.8, 2.0))
        add_part('cube', RED, (2.7, 0.15, 0.1), (0, 1.2, 0.1))
        add_part('cube', RED, (2.7, 0.15, 0.1), (0, 0.4, 0.1))
        add_part('cube', BLACK, (0.1, 1.4, 2.6), (0, 0.8, 4.05))
        add_part('cube', color.rgb(30/255, 60/255, 180/255), (2.6, 0.1, 3.8), (0, 1.6, 2.0))

        # Wheels
        make_cylinder(0.25, 0.15, BLACK, (-0.8, 0.2, 0.6), rot=(90,0,0), parent=self.truck)
        make_cylinder(0.25, 0.15, BLACK, ( 0.8, 0.2, 0.6), rot=(90,0,0), parent=self.truck)
        for z in [1.6, 2.8]:
            for x in [-0.9, 0.9]:
                make_cylinder(0.25, 0.15, BLACK, (x, 0.2, z), rot=(90,0,0), parent=self.truck)
        for z in [0.6, 1.6, 2.8]:
            for x in [-0.8, 0.8]:
                make_cylinder(0.08, 0.02, SILVER, (x, 0.2, z), rot=(90,0,0), parent=self.truck)
        add_part('cube', RED, (1.0, 0.15, 0.6), (-0.8, 0.4, 0.6))
        add_part('cube', RED, (1.0, 0.15, 0.6), ( 0.8, 0.4, 0.6))
        for z in [1.6, 2.8]:
            add_part('cube', RED, (1.0, 0.15, 0.6), (-0.9, 0.4, z))
            add_part('cube', RED, (1.0, 0.15, 0.6), ( 0.9, 0.4, z))

        self.truck.position = (0, -0.2, 0)

        # ---------- PLANE – built along Z (forward) ----------
        self.plane = Entity(parent=self, enabled=False)
        plane_scale = 1.5

        def add_plane_part(model, col, scale, pos, rot=(0,0,0)):
            # Convert tuples to Vec3 to allow multiplication
            if isinstance(scale, tuple):
                scale = Vec3(*scale)
            if isinstance(pos, tuple):
                pos = Vec3(*pos)
            return Entity(
                model=model,
                color=col,
                scale=scale * plane_scale,
                position=pos * plane_scale,
                rotation=rot,
                parent=self.plane
            )

        # Fuselage (white with red stripe) – length along Z
        add_plane_part('cube', color.white, (0.8, 0.6, 2.0), (0, 0.0, 0))
        add_plane_part('cube', RED, (0.82, 0.05, 1.8), (0, 0.0, 0))
        # Cockpit (cyan) – forward
        add_plane_part('cube', color.cyan, (0.4, 0.3, 0.5), (0, 0.4, 0.8))
        # Main wings – extend along X
        add_plane_part('cube', color.gray, (3.0, 0.05, 0.1), (0, 0.1, 0))
        add_plane_part('cube', color.gray, (3.0, 0.05, 0.1), (0, -0.1, 0))
        # Red wing tips
        add_plane_part('cube', RED, (0.4, 0.05, 0.1), (1.6, 0.1, 0))
        add_plane_part('cube', RED, (0.4, 0.05, 0.1), (-1.6, 0.1, 0))
        add_plane_part('cube', RED, (0.4, 0.05, 0.1), (1.6, -0.1, 0))
        add_plane_part('cube', RED, (0.4, 0.05, 0.1), (-1.6, -0.1, 0))
        # Tail (orange) – behind
        add_plane_part('cube', color.orange, (0.1, 0.4, 0.6), (0, 0.2, -0.9))
        add_plane_part('cube', color.orange, (0.4, 0.5, 0.1), (0, 0.6, -0.9))
        # Engines (dark gray) – at the back
        add_plane_part('cube', color.dark_gray, (0.15, 0.2, 0.15), (-0.4, 0.0, -0.8))
        add_plane_part('cube', color.dark_gray, (0.15, 0.2, 0.15), ( 0.4, 0.0, -0.8))
        # Wing lights (yellow spheres)
        add_plane_part('sphere', YELLOW, 0.12, (1.6, 0.1, 0))
        add_plane_part('sphere', YELLOW, 0.12, (-1.6, 0.1, 0))
        add_plane_part('sphere', YELLOW, 0.12, (1.6, -0.1, 0))
        add_plane_part('sphere', YELLOW, 0.12, (-1.6, -0.1, 0))
        # Headlights
        add_plane_part('sphere', color.yellow, 0.1, (0, 0.0, 1.0))
        add_plane_part('sphere', color.yellow, 0.1, (0.4, 0.0, 1.0))
        add_plane_part('sphere', color.yellow, 0.1, (-0.4, 0.0, 1.0))

        # Engine exhaust flame – use a cylinder instead of a cone (avoid missing model warning)
        self.engine_flame_left = make_cylinder(
            radius=0.15,
            height=0.3,
            color=color.yellow,
            pos=(-0.4 * plane_scale, 0.0, -0.9 * plane_scale),
            rot=(90, 0, 0),
            parent=self.plane
        )
        self.engine_flame_left.enabled = False
        self.engine_flame_right = make_cylinder(
            radius=0.15,
            height=0.3,
            color=color.yellow,
            pos=(0.4 * plane_scale, 0.0, -0.9 * plane_scale),
            rot=(90, 0, 0),
            parent=self.plane
        )
        self.engine_flame_right.enabled = False

        self.plane.position = (0, -0.2 * plane_scale, 0)

        self.walk_time = 0
        self.walk_speed = 8

        self.shield_entity = Entity(model='sphere', color=Color(0, 1, 1, 0.3), scale=2,
                                    position=(0,1,0), parent=self, enabled=False)

        self.pickup_prompt = Text(text='', position=(0,-0.35), scale=1.5, origin=(0,0), color=color.gold, enabled=False)

        self.robot.enabled = True
        self.truck.enabled = False
        self.plane.enabled = False

    def update(self):
        # Only run game logic if we are in playing state
        global game_state
        if game_state != 'playing':
            return

        if game_over:
            return
        update_day_night()

        # Cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= time.dt
        if self.melee_cooldown > 0:
            self.melee_cooldown -= time.dt
        if self.dash_cooldown > 0:
            self.dash_cooldown -= time.dt
        if self.matrix_cooldown > 0:
            self.matrix_cooldown -= time.dt
        if self.invincible_timer > 0:
            self.invincible_timer -= time.dt
            if self.invincible_timer <= 0:
                self.invincible = False
        if self.matrix_boost_timer > 0:
            self.matrix_boost_timer -= time.dt
            if self.matrix_boost_timer <= 0:
                self.matrix_boost = False
                self.matrix_glow.color = CYAN

        if self.dashing:
            self.dash_timer -= time.dt
            if self.dash_timer <= 0:
                self.dashing = False
                self.speed = self.original_speed

        move = Vec3(held_keys['d']-held_keys['a'], 0, held_keys['w']-held_keys['s'])

        if self.mode == 'plane':
            # Enable engine flames when moving forward
            if held_keys['w']:
                self.engine_flame_left.enabled = True
                self.engine_flame_right.enabled = True
            else:
                self.engine_flame_left.enabled = False
                self.engine_flame_right.enabled = False

            if held_keys['w']:
                self.position += self.forward * self.speed * time.dt
            if held_keys['s']:
                self.position -= self.forward * self.speed * time.dt * 0.5
            if held_keys['a']:
                self.rotation_y += 120 * time.dt
            if held_keys['d']:
                self.rotation_y -= 120 * time.dt
            if held_keys['space']:
                self.position.y += self.speed * time.dt * 0.8
            if held_keys['shift']:
                self.position.y -= self.speed * time.dt * 0.8
            self.rotation_x = 0
            self.rotation_z = 0
            if self.position.y < 0.5:
                self.position.y = 0.5
            for part in (self.left_arm, self.right_arm, self.left_forearm, self.right_forearm,
                         self.left_thigh, self.right_thigh, self.left_shin, self.right_shin):
                part.rotation_x = 0
            self.robot.y = 0
        else:
            self.engine_flame_left.enabled = False
            self.engine_flame_right.enabled = False
            current_speed = self.speed if self.mode == 'robot' else self.truck_speed
            moving = move.length() > 0

            self.vertical_speed -= self.gravity * time.dt
            self.y += self.vertical_speed * time.dt
            if self.y < 1:
                self.y = 1
                self.vertical_speed = 0

            if moving:
                move = move.normalized()
                movement = move * current_speed * time.dt
                move_entity_with_collision(self, movement, obstacles)

                self.target_rotation_y = math.degrees(math.atan2(move.x, move.z))
                self.rotation_y = lerp(self.rotation_y, self.target_rotation_y, time.dt * 10)

                if self.mode == 'robot' and not self.dashing:
                    speed_factor = current_speed / 8
                    self.walk_time += time.dt * self.walk_speed * speed_factor
                    swing = math.sin(self.walk_time) * 30
                    self.left_arm.rotation_x = swing
                    self.right_arm.rotation_x = -swing
                    self.left_forearm.rotation_x = swing * 0.5
                    self.right_forearm.rotation_x = -swing * 0.5
                    self.left_thigh.rotation_x = -swing * 0.7
                    self.right_thigh.rotation_x = swing * 0.7
                    self.left_shin.rotation_x = swing * 0.5
                    self.right_shin.rotation_x = -swing * 0.5
                    self.robot.y = abs(math.sin(self.walk_time)) * 0.06
            else:
                if self.mode == 'robot':
                    for part in (self.left_arm, self.right_arm, self.left_forearm, self.right_forearm):
                        part.rotation_x = 0
                    for part in (self.left_thigh, self.right_thigh, self.left_shin, self.right_shin):
                        part.rotation_x = 0
                    self.robot.y = 0

        if self.shield_active:
            self.shield_entity.enabled = True
        else:
            self.shield_entity.enabled = False

        if mouse.left and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = .15

        if held_keys['q'] and self.melee_cooldown <= 0 and self.mode == 'robot':
            self.melee_attack()
            self.melee_cooldown = 0.5

        if held_keys['shift'] and self.dash_cooldown <= 0 and not self.dashing and self.mode == 'robot':
            self.dash()
            self.dash_cooldown = 1.0

        if held_keys['e'] and self.matrix_cooldown <= 0 and self.mode == 'robot':
            self.activate_matrix()
            self.matrix_cooldown = 30

        nearby = False
        for pickup in resource_pickups + health_packs:
            if distance(self.position, pickup.position) < 2.0:
                nearby = True
                break
        if nearby and not game_over:
            self.pickup_prompt.text = "Press R to pick up"
            self.pickup_prompt.enabled = True
        else:
            self.pickup_prompt.enabled = False

    def shoot(self):
        if self.mode == 'robot':
            muzzle_flash(self.world_position + Vec3(1.0,1.1,0))
            Bullet(self.world_position + Vec3(0,1.5,0), camera.forward, damage=20 if self.matrix_boost else 10)
            self.right_arm.rotation_x = -25
            self.right_arm.animate('rotation_x', 0, duration=.12, curve=curve.out_expo)
        else:
            shoot_pos = self.world_position + self.forward * 2.5 + Vec3(0, 0.6, 0)
            muzzle_flash(shoot_pos)
            Bullet(shoot_pos, camera.forward, damage=20 if self.matrix_boost else 10)

    def melee_attack(self):
        try:
            self.axe.enabled = True
            self.axe.rotation_z = -90
            self.axe.animate('rotation_z', 90, duration=0.2, curve=curve.out_quad)
            invoke(setattr, self.axe, 'enabled', False, delay=0.2)

            for enemy in enemies[:]:
                dir_to_enemy = (enemy.position - self.position).normalized()
                forward = self.forward
                if Vec3.dot(dir_to_enemy, forward) > 0.7 and distance(self.position, enemy.position) < 4:
                    enemy.take_damage(30 if self.matrix_boost else 15)
                    particle_burst(enemy.position, count=8, color=color.cyan)

            for target in tree_entities + rock_entities:
                if distance(self.position, target.position) < 3:
                    target.health -= 15 if self.matrix_boost else 10
                    particle_burst(target.position, count=4, color=color.white)
                    if target.health <= 0:
                        if target in tree_entities:
                            ResourcePickup(target.position, 'wood')
                            if hasattr(target, 'parent_entity'):
                                destroy(target.parent_entity)
                            destroy(target)
                            tree_entities.remove(target)
                            update_obstacles()
                            invoke(lambda: respawn_tree(target.position), delay=10)
                        elif target in rock_entities:
                            ResourcePickup(target.position, 'stone')
                            destroy(target)
                            rock_entities.remove(target)
                            update_obstacles()
                            invoke(lambda: respawn_rock(target.position), delay=15)

            slash = Entity(
                model='cube',
                color=color.cyan,
                scale=(2, 0.2, 0.5),
                position=self.position + self.forward * 2 + Vec3(0, 0.5, 0),
                rotation=(0, self.rotation_y, 0)
            )
            slash.animate_scale((3, 0.2, 0.5), duration=0.15)
            slash.animate_color(Color(0,0,0,0), duration=0.15)
            destroy(slash, delay=0.15)
        except Exception as e:
            print(f"Melee error: {e}")
            import traceback
            traceback.print_exc()

    def dash(self):
        self.dashing = True
        self.dash_timer = 0.3
        self.invincible = True
        self.invincible_timer = 0.3
        self.original_speed = self.speed
        self.speed = 30
        direction = self.forward
        if held_keys['w'] or held_keys['s'] or held_keys['a'] or held_keys['d']:
            move = Vec3(held_keys['d']-held_keys['a'], 0, held_keys['w']-held_keys['s'])
            if move.length() > 0:
                direction = move.normalized()
        movement = direction * 8
        move_entity_with_collision(self, movement, obstacles)

    def activate_matrix(self):
        try:
            self.health = min(self.max_health, self.health + 50)
            self.matrix_boost = True
            self.matrix_boost_timer = 5
            self.matrix_glow.color = GOLD
            flash = Entity(model='sphere', color=GOLD, scale=4, position=self.position)
            flash.animate_scale(0, duration=0.5)
            flash.animate_color(Color(0,0,0,0), duration=0.5)
            destroy(flash, delay=0.5)
            particle_burst(self.position, count=20, color=GOLD, speed=4)
        except Exception as e:
            print(f"Matrix error: {e}")

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def pickup_nearby(self):
        for pickup in resource_pickups[:]:
            if distance(self.position, pickup.position) < 2.0:
                collect_resource(pickup)
        for pack in health_packs[:]:
            if distance(self.position, pack.position) < 2.0:
                collect_health_pack(pack)

    def input(self, key):
        global game_state
        if game_state != 'playing':
            return
        if key == 'space' and self.y <= 1.01 and not game_over and self.mode == 'robot':
            self.vertical_speed = self.jump_speed
        if key == 'f' and not game_over:
            self.transform()
        if key == 'right mouse down' and self.mode == 'robot':
            self.shield_active = True
        if key == 'right mouse up':
            self.shield_active = False
        if key == 'r':
            if game_over:
                respawn()
            else:
                self.pickup_nearby()

    def transform(self):
        try:
            self.dashing = False
            self.speed = self.original_speed if self.mode == 'robot' else self.truck_speed

            if self.mode == 'robot':
                self.mode = 'truck'
            elif self.mode == 'truck':
                self.mode = 'plane'
            else:
                self.mode = 'robot'

            self.robot.enabled = (self.mode == 'robot')
            self.truck.enabled = (self.mode == 'truck')
            self.plane.enabled = (self.mode == 'plane')

            if self.mode == 'robot':
                self.walk_time = 0
                for part in (self.left_arm, self.right_arm, self.left_forearm, self.right_forearm,
                             self.left_thigh, self.right_thigh, self.left_shin, self.right_shin):
                    part.rotation = (0,0,0)
                self.robot.y = 0

            self.collider = None
            if self.mode == 'robot':
                self.collider = BoxCollider(self, center=(0, 0.5, 0), size=(1.2, 1.8, 0.8))
                camera.position = (0, 8, -18)
                camera.rotation_x = 20
            elif self.mode == 'truck':
                self.collider = BoxCollider(self, center=(0, 0.6, 1.2), size=(2.4, 1.2, 3.6))
                camera.position = (0, 4, -12)
                camera.rotation_x = 15
            else:
                self.collider = BoxCollider(self, center=(0, 0.3, 0), size=(2.2, 0.8, 3.2))
                camera.position = (0, 6, -22)
                camera.rotation_x = 12

            explosion(self.position, c=color.white, size=2.5)
            particle_burst(self.position, count=20, color=color.cyan, speed=3)
        except Exception as e:
            print(f"Transform error: {e}")

# ==========================
# RESPAWN FUNCTIONS
# ==========================
def respawn_tree(pos):
    x, z = pos.x + uniform(-1,1), pos.z + uniform(-1,1)
    if -75 < x < 75 and -75 < z < 75:
        t, c = create_tree(x, z)
        trees.append((t, c))
        update_obstacles()

def respawn_rock(pos):
    x, z = pos.x + uniform(-1,1), pos.z + uniform(-1,1)
    if -70 < x < 70 and -70 < z < 70:
        r = create_rock(x, z)
        rocks.append(r)
        update_obstacles()

# ==========================
# BULLETS
# ==========================
class Bullet(Entity):
    def __init__(self, position, direction, damage=10):
        super().__init__(model='sphere', color=color.yellow, scale=.3, position=position)
        self.direction = direction.normalized()
        self.speed = 50
        self.damage = damage
        self.trail_timer = 0
        Entity(parent=self, model='sphere', color=color.rgb(1,.8,.2), scale=.8)
        destroy(self, delay=3)

    def update(self):
        self.position += self.direction * self.speed * time.dt
        self.trail_timer += time.dt
        if self.trail_timer > .02:
            self.trail_timer = 0
            t = Entity(model='sphere', color=color.yellow, scale=.1, position=self.position)
            t.animate_scale(0, duration=.2)
            t.animate_color(Color(0,0,0,0), duration=.2)
            destroy(t, delay=.2)
        for enemy in enemies[:]:
            if distance(self.position, enemy.position) < 1.5:
                enemy.take_damage(self.damage)
                explosion(enemy.position + Vec3(uniform(-.5,.5),uniform(-.5,.5),uniform(-.5,.5)))
                destroy(self)
                return

class EnemyBullet(Entity):
    def __init__(self, position, direction):
        super().__init__(model='sphere', color=color.red, scale=.2, position=position)
        self.direction = direction.normalized()
        self.speed = 15
        destroy(self, delay=5)

    def update(self):
        self.position += self.direction * self.speed * time.dt
        if distance(self.position, player.position) < 1.5:
            player.take_damage(0.1)
            destroy(self)

# ==========================
# MEGATRON (boss with tank transformation)
# ==========================
DEC_PURPLE = color.rgb(110/255,  0/255, 170/255)
DEC_GRAY   = color.rgb( 75/255, 78/255,  88/255)
DEC_RED    = color.rgb(210/255,  0/255,   0/255)

class Enemy(Entity):
    def __init__(self, is_boss=False):
        super().__init__(position=(uniform(-40,40), 1, uniform(-40,40)), collider='box')
        self.is_boss = is_boss

        if is_boss:
            # Megatron – robot mode
            self.health = 500
            self.max_health = 500
            self.speed = 2.5
            self.damage = 20
            self.scale = 1.5
            self.mode = 'robot'
            self.transformed = False

            self.robot_entity = Entity(parent=self)
            self.tank_entity = Entity(parent=self, enabled=False)

            # Build robot
            def ep(col, sc, pos):
                Entity(model='cube', color=col, scale=sc, position=pos, parent=self.robot_entity)
            ep(MEGATRON_GRAY, (2.0, 2.5, 1.2), (0, 1.8, 0))
            ep(MEGATRON_PURPLE, (1.0, 0.4, 0.8), (-1.2, 2.4, 0))
            ep(MEGATRON_PURPLE, (1.0, 0.4, 0.8), ( 1.2, 2.4, 0))
            ep(MEGATRON_GRAY, (0.8, 0.8, 0.6), (0, 3.2, 0))
            ep(MEGATRON_RED, (0.2, 0.1, 0.3), (-0.3, 3.4, 0.4))
            ep(MEGATRON_RED, (0.2, 0.1, 0.3), ( 0.3, 3.4, 0.4))
            ep(MEGATRON_PURPLE, (0.6, 1.2, 0.6), (-1.6, 1.6, 0))
            ep(MEGATRON_GRAY, (0.8, 0.6, 0.6), ( 1.6, 1.6, 0))
            ep(MEGATRON_GRAY, (0.8, 1.2, 0.8), (-0.8, 0.6, 0))
            ep(MEGATRON_GRAY, (0.8, 1.2, 0.8), ( 0.8, 0.6, 0))
            # Fusion cannon – use make_cylinder helper
            make_cylinder(0.2, 0.6, MEGATRON_PURPLE, (-1.8, 1.8, 0.4), rot=(0,0,90), parent=self.robot_entity)

            # Build tank model
            def add_tank_part(model, col, scale, pos, rot=(0,0,0)):
                Entity(model=model, color=col, scale=scale, position=pos, rotation=rot, parent=self.tank_entity)

            add_tank_part('cube', MEGATRON_DARK, (2.8, 1.0, 1.8), (0, 0.5, 0))
            add_tank_part('cube', MEGATRON_GRAY, (1.2, 0.6, 1.2), (0, 1.2, 0))
            add_tank_part('cube', MEGATRON_GRAY, (0.2, 0.2, 1.2), (0, 1.2, 1.0), rot=(0,0,0))
            add_tank_part('cube', BLACK, (2.6, 0.3, 0.4), (-1.5, 0.3, 0))
            add_tank_part('cube', BLACK, (2.6, 0.3, 0.4), ( 1.5, 0.3, 0))
            for x in [-1.5, 1.5]:
                for z in [-0.8, -0.4, 0, 0.4, 0.8]:
                    make_cylinder(0.2, 0.1, MEGATRON_GRAY, (x, 0.2, z), rot=(0,90,0), parent=self.tank_entity)
            add_tank_part('cube', MEGATRON_RED, (0.6, 0.08, 0.05), (0, 0.8, 1.0))

            bg = Entity(parent=self, model='cube', color=color.black, scale=(1.8, .15, .1), position=(0, 4.2, 0))
            self.health_bar_bg = bg
            self.health_bar = Entity(parent=bg, model='cube', color=color.lime, scale=(1, 1, 1), position=(0, 0, .01))

            self.announce_text = Text(text='MEGATRON APPEARS!', position=(0, 0.3), scale=2, color=color.red, origin=(0,0))
            destroy(self.announce_text, delay=2)

        else:
            # Normal enemy
            self.health = 100
            self.max_health = 100
            self.speed = 3
            self.damage = 10
            self.scale = 1
            self.mode = 'robot'
            self.transformed = False
            r = Entity(parent=self)
            def ep(col, sc, pos):
                Entity(model='cube', color=col, scale=sc, position=pos, parent=r)
            ep(DEC_PURPLE, (1.2, 1.4, .7), (0, 1.3, 0))
            ep(DEC_RED,    (.5, .3, .12), (0, 1.5, .37))
            ep(DEC_GRAY,   (.9, .22, .5), (0, .6, 0))
            ep(DEC_GRAY,   (.52, .48, .46), (0, 2.25, 0))
            ep(DEC_RED,    (.42, .14, .08), (0, 2.3, .25))
            ep(DEC_GRAY,   (.08, .28, .08), (-.18, 2.58, 0))
            ep(DEC_GRAY,   (.08, .28, .08), (.18, 2.58, 0))
            ep(DEC_PURPLE, (.28, .9, .28), (-.75, 1.2, 0))
            ep(DEC_PURPLE, (.28, .9, .28), (.75, 1.2, 0))
            ep(DEC_GRAY,   (.32, .85, .32), (-.3, .1, 0))
            ep(DEC_GRAY,   (.32, .85, .32), (.3, .1, 0))
            bg = Entity(parent=self, model='cube', color=color.black, scale=(1.2,.1,.1), position=(0, 3.8, 0))
            self.health_bar_bg = bg
            self.health_bar = Entity(parent=bg, model='cube', color=color.lime, scale=(1,1,1), position=(0,0,.01))

        self.shoot_timer = uniform(1,3) if not is_boss else uniform(0.5, 1.2)

    def transform_to_tank(self):
        if self.transformed or not self.is_boss:
            return
        self.transformed = True
        self.mode = 'tank'
        self.robot_entity.enabled = False
        self.tank_entity.enabled = True
        self.speed = 3.5
        self.damage = 30
        self.shoot_timer = 0.3
        explosion(self.position, c=color.orange, size=4)
        particle_burst(self.position, count=30, color=color.purple, speed=3)
        trans_text = Text(text='MEGATRON TRANSFORMS TO TANK!', position=(0, 0.2), scale=2, color=color.orange, origin=(0,0))
        destroy(trans_text, delay=2)

    def update(self):
        # Only run game logic if playing
        global game_state
        if game_state != 'playing':
            return

        if self.is_boss and not self.transformed and self.health <= self.max_health * 0.5:
            self.transform_to_tank()

        hp = max(self.health/self.max_health, 0)
        self.health_bar.scale_x = hp
        self.health_bar.color = color.rgb(1-hp, hp, 0)

        d = player.position - self.position
        d.y = 0
        if d.length() > 1:
            direction = d.normalized()
            movement = direction * self.speed * time.dt
            move_entity_with_collision(self, movement, obstacles)
            self.look_at(player)

        if distance(self, player) < 1.5:
            player.take_damage(self.damage * time.dt)

        self.shoot_timer -= time.dt
        if self.shoot_timer <= 0 and distance(self, player) < 30:
            dir = (player.position - self.position).normalized()
            if self.is_boss and self.mode == 'tank':
                EnemyBullet(self.position + Vec3(0,1,0), dir)
                EnemyBullet(self.position + Vec3(0,1,0), dir + Vec3(0, 0.1, 0))
            else:
                EnemyBullet(self.position + Vec3(0,1,0), dir)
            self.shoot_timer = uniform(1.5, 3) if not self.is_boss else (0.3 if self.mode=='tank' else uniform(0.5, 1.2))
            muzzle_flash(self.position + Vec3(0,1,0))

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        global score, combo, max_combo, megatron_defeated
        if mission.type == 'kill' and not mission.completed:
            mission.progress += 1
            if mission.progress >= mission.target:
                mission.complete()

        for _ in range(4):
            explosion(self.position+Vec3(uniform(-1,1),uniform(-1,1),uniform(-1,1)), color.red, size=2)
        particle_burst(self.position, count=15, color=color.orange, speed=2)
        combo += 1
        if combo > max_combo:
            max_combo = combo
        score += 10 * combo
        if self.is_boss:
            score += 200
            megatron_defeated = True
            victory_text = Text(text='VICTORY! MEGATRON DEFEATED!', position=(0, 0.1), scale=3, color=GOLD, origin=(0,0))
            global game_over
            game_over = True
        if self in enemies:
            enemies.remove(self)
        destroy(self)

# ==========================
# HEALTH PACK
# ==========================
class HealthPack(Entity):
    def __init__(self):
        super().__init__(model='sphere', color=color.green, scale=0.4,
                         position=(uniform(-50,50), 0.5, uniform(-50,50)), collider='sphere')
        self.rotation_y = 0

    def update(self):
        self.rotation_y += 100 * time.dt

# ==========================
# SPAWN LOGIC
# ==========================
def spawn_enemy():
    global megatron_defeated
    if megatron_defeated:
        if uniform(0,1) < 0.3:
            enemy = Enemy(is_boss=False)
            enemies.append(enemy)
        return

    if mission.level >= 5 and not any(e.is_boss for e in enemies):
        enemy = Enemy(is_boss=True)
        enemies.append(enemy)
    else:
        if uniform(0,1) < 0.15:
            enemy = Enemy(is_boss=False)
        else:
            enemy = Enemy(is_boss=False)
        enemies.append(enemy)

def spawn_health_pack():
    hp = HealthPack()
    health_packs.append(hp)

for _ in range(6):
    spawn_enemy()
for _ in range(2):
    spawn_health_pack()

# ==========================
# PLAYER INSTANCE
# ==========================
player = Player()
camera.parent = player
camera.position = (0, 8, -18)
camera.rotation_x = 20

# ==========================
# UI
# ==========================
health_text    = Text(text='', position=(-.86,.45), scale=1.3, origin=(0,0))
score_text     = Text(text='', position=(-.86,.40), scale=1.3, origin=(0,0))
combo_text     = Text(text='', position=(-.86,.35), scale=1.3, origin=(0,0), color=color.orange)
cooldown_text  = Text(text='', position=(-.86,.30), scale=1.0, origin=(0,0), color=color.cyan)
mission_text   = Text(text='', position=(-.86,.25), scale=1.0, origin=(0,0), color=GOLD)
mission_progress = Text(text='', position=(-.86,.20), scale=1.0, origin=(0,0), color=GOLD)
inventory_text = Text(text='', position=(-.86,.15), scale=1.0, origin=(0,0), color=color.white)
mission_complete_text = Text(text='', position=(0,.12), scale=2, origin=(0,0), color=GOLD, enabled=False)
hint_text      = Text(text='[LMB] Shoot  |  [Q] Melee/Cut  |  [Shift] Dash  |  [RMB] Shield  |  [E] Matrix  |  [F] Transform  |  [R] Pick up',
                      position=(0,-.46), scale=1.0, origin=(0,0), color=color.white)
game_over_text = Text(text='', origin=(0,0), position=(0,.08), scale=4, color=color.red, enabled=False)
respawn_prompt = Text(text='Press R to Respawn', origin=(0,0), position=(0,-.05), scale=2, color=color.white, enabled=False)
victory_text = Text(text='', origin=(0,0), position=(0,0), scale=3, color=GOLD, enabled=False)

# ==========================
# MENU BUTTON (in-game, top-right) – kept for pause/menu
# ==========================
menu_button = Button(
    text='Menu',
    position=(0.85, 0.45),
    scale=(0.1, 0.05),
    color=color.gray,
    text_color=color.white,
    enabled=True          # now enabled at start (game is playing)
)

# ==========================
# MAIN MENU (still exists, but disabled initially)
# ==========================
menu_panel = Panel(
    parent=camera.ui,
    color=color.rgb(10, 10, 25),
    scale=(2, 2),
    position=(0, 0),
    z=0,
    enabled=False          # hidden at start
)

title = Text(
    text='Transformers: Cyber Battle',
    parent=menu_panel,
    position=(0, 0.35),
    scale=2.5,
    origin=(0,0),
    color=GOLD,
    z=1
)

button_scale = (0.8, 0.15)
button_pos = (0, 0.0)

start_button = Button(
    text='Start Game',
    parent=menu_panel,
    position=button_pos,
    scale=button_scale,
    color=color.blue,
    text_color=color.white,
    text_scale=1.2,
    z=1
)

def on_hover():
    start_button.color = GOLD
    start_button.scale = (button_scale[0]*1.05, button_scale[1]*1.05)
    start_button.text_color = color.black

def on_hover_end():
    start_button.color = color.blue
    start_button.scale = button_scale
    start_button.text_color = color.white

start_button.on_mouse_enter = on_hover
start_button.on_mouse_exit = on_hover_end

# start_game function still exists but we won't use it initially
def start_game():
    global game_state
    game_state = 'playing'
    menu_panel.enabled = False
    menu_button.enabled = True
    for elem in [health_text, score_text, combo_text, cooldown_text, mission_text,
                 mission_progress, inventory_text, hint_text, game_over_text, victory_text]:
        elem.enabled = True
    mission_complete_text.enabled = False

start_button.on_click = start_game

def show_menu():
    menu_panel.enabled = True
    menu_button.enabled = False
    for elem in [health_text, score_text, combo_text, cooldown_text, mission_text,
                 mission_progress, inventory_text, hint_text, game_over_text, victory_text]:
        elem.enabled = False
    mission_complete_text.enabled = False

def go_to_menu():
    global game_state
    game_state = 'menu'
    show_menu()

menu_button.on_click = go_to_menu

# ---- Start the game directly ----
# Enable in‑game UI and disable menu panel
game_state = 'playing'
menu_panel.enabled = False
menu_button.enabled = True
for elem in [health_text, score_text, combo_text, cooldown_text, mission_text,
             mission_progress, inventory_text, hint_text, game_over_text, victory_text]:
    elem.enabled = True
mission_complete_text.enabled = False

# ==========================
# RESPAWN
# ==========================
def respawn():
    global score, combo, max_combo, game_over, spawn_timer, health_pack_timer, mission, megatron_defeated
    player.health = 1000000
    player.position = Vec3(0,1,0)
    player.vertical_speed = 0
    score = 0
    combo = 0
    max_combo = 0
    spawn_timer = 0
    health_pack_timer = 0
    megatron_defeated = False
    mission = Mission()
    for e in enemies[:]: destroy(e)
    enemies.clear()
    for hp in health_packs[:]: destroy(hp)
    health_packs.clear()
    for _ in range(6): spawn_enemy()
    for _ in range(2): spawn_health_pack()
    game_over_text.enabled = False
    respawn_prompt.enabled = False
    victory_text.enabled = False
    game_over = False

# ==========================
# MAIN UPDATE
# ==========================
def update():
    global spawn_timer, health_pack_timer, game_over, score, combo, megatron_defeated, game_state

    if game_state == 'menu':
        return  # nothing to update

    mission.update(player, enemies, health_packs)

    health_text.text = f"HP: {int(player.health)}"
    score_text.text  = f"Score:  {score}"
    combo_text.text  = f"Combo: x{combo}" if combo > 1 else ""
    cd_text = ""
    if player.matrix_cooldown > 0:
        cd_text += f"Matrix: {int(player.matrix_cooldown)}s "
    if player.dash_cooldown > 0:
        cd_text += f"Dash: {int(player.dash_cooldown)}s "
    cooldown_text.text = cd_text

    inventory_text.text = f"Wood: {inventory['wood']}  Stone: {inventory['stone']}"

    if mission.completed:
        mission_text.text = "Mission Complete!"
        mission_progress.text = ""
    else:
        mission_text.text = f"Mission: {mission.description}"
        mission_progress.text = f"Progress: {mission.get_progress_text()}"

    if megatron_defeated:
        victory_text.text = 'YOU WIN!'
        victory_text.enabled = True
        return

    if not game_over:
        spawn_timer += time.dt
        if spawn_timer > 6:
            spawn_enemy()
            spawn_timer = 0
        health_pack_timer += time.dt
        if health_pack_timer > 12 and len(health_packs) < 4:
            spawn_health_pack()
            health_pack_timer = 0

    if player.health <= 0 and not game_over:
        game_over_text.text = 'GAME OVER'
        game_over_text.enabled = True
        respawn_prompt.enabled = True
        game_over = True

# ==========================
# INPUT
# ==========================
def input(key):
    global game_state
    if key == 'escape':
        if game_state == 'playing':
            go_to_menu()
    if game_state == 'menu':
        return
    if key == 'r' and game_over:
        respawn()

app.run()
