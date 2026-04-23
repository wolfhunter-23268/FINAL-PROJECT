import random
import pgzrun
from pgzhelper import Actor
import pygame

WIDTH = 800
HEIGHT = 600

SCALE = 3

# DEV TOOLS
show_hitboxes = False  # Set to True to show all hitboxes
test_speed_modifier = False   # Set to True to increce player speed
give_all_items = False       # Set to True to give the player all items at game start

# Final room animation state
final_room_mode = False
final_room_frame = 0
final_room_timer = 0
final_room_images = [f"final room{i}.png" for i in range(0, 6)]  # Adjust range as needed
final_room_frame_delay = 10  # Frames per animation frame

# Preload the interaction hitbox image (original and scaled cache)
hitbox_img_original = pygame.image.load("images/HITBOX-1.png.png")
hitbox_img_cache = {}

# Track last room for hitbox cache
last_hitbox_room = None
room_hitbox_cache = {}

# Interaction and room system
class Interaction:
    def __init__(self, source_room, x, y, width, height, target_room, target_x, target_y, show_hitbox=True, axe_required=False, item1_required=False, item2_required=False, 
                 item3_required=False, item6_required=False, item5_required=False, item0_required=False):
        self.source_room = source_room
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.target_room = target_room
        self.target_x = target_x
        self.target_y = target_y
        self.show_hitbox = show_hitbox
        self.axe_required = axe_required
        self.item1_required = item1_required
        self.item3_required = item3_required
        self.item2_required = item2_required
        self.item6_required = item6_required
        self.item5_required = item5_required
        self.item0_required = item0_required

    def is_on(self, px, py):
        return (self.x <= px <= self.x + self.width and
                self.y - self.height//2 <= py <= self.y + self.height//2)



# Helper to add interactions only for connected directions
def make_room_interactions(current_room, left, right, bottom, top):

    if left:
        axe_required = (current_room == "Map15-1.png.png" and left == "Map16-1.png.png")
        item2_required = (current_room == "Map14-1.png.png" and left == "Map06-1.png.png")
        interactions.append(Interaction(current_room, 0, HEIGHT//1.8, 60, 100, left, WIDTH-80, HEIGHT//2, axe_required=axe_required, item2_required=item2_required))
    if right:
        interactions.append(Interaction(current_room, WIDTH-60, HEIGHT//1.8, 60, 100, right, 80, HEIGHT//2))
    if bottom:
        item1_required = (current_room == "Map13-1.png.png" and bottom == "Map17-1.png.png")
        item3_required = (current_room == "Map16-1.png.png" and bottom == "Map07-1.png.png")
        item6_required = (current_room == "Map07-1.png.png" and bottom == "Map10-1.png.png")
        item5_required = (current_room == "Map14-1.png.png" and bottom == "Map11-1.png.png")
        interactions.append(Interaction(current_room, WIDTH//2.3, HEIGHT-60, 100, 60, bottom, WIDTH//2, 80, item1_required=item1_required, item3_required=item3_required, 
                                        item6_required=item6_required, item5_required=item5_required))
    if top:
        interactions.append(Interaction(current_room, WIDTH//2.3, 125, 100, 60, top, WIDTH//2, HEIGHT-100))
    return interactions

left=None
right=None
bottom=None
top=None

interactions = []
# Starting room (background.png)
interactions += make_room_interactions("background.png", left="Map12-1.png.png", right="Map13-1.png.png", bottom="Map15-1.png.png", top=None)
# Map12-1.png.png (below start)
interactions += make_room_interactions("Map12-1.png.png", left=None, right="background.png", bottom=None, top=None)
# Map13-1.png.png (right of start)
interactions += make_room_interactions("Map13-1.png.png",  left="background.png", right=None, bottom="Map17-1.png.png", top=None)
# Map17-1.png.png (below Map13)
interactions += make_room_interactions("Map17-1.png.png",  left=None, right=None, bottom="Map14-1.png.png", top="Map13-1.png.png",)
# Map15-1.png.png (left of Map17)
interactions += make_room_interactions("Map15-1.png.png", right=None, left="Map16-1.png.png", top="background.png", bottom=None)
# Map16-1.png.png (left of Map15)
interactions += make_room_interactions("Map16-1.png.png", right="Map15-1.png.png", bottom="Map07-1.png.png", top=None, left=None)
# Map07-1.png.png (below Map16)
interactions += make_room_interactions("Map07-1.png.png", top="Map16-1.png.png", right=None, left=None, bottom="Map10-1.png.png")
# Map06-1.png.png (right of Map07)
interactions += make_room_interactions("Map06-1.png.png", left=None, right="Map14-1.png.png", top=None, bottom="Map09-1.png.png")
# Map14-1.png.png (right of Map06)
interactions += make_room_interactions("Map14-1.png.png", left="Map06-1.png.png", bottom="Map11-1.png.png", top="Map17-1.png.png", right=None)
# Map11-1.png.png (below Map14)
interactions += make_room_interactions("Map11-1.png.png", top="Map14-1.png.png", left=None, right=None, bottom=None)
# Map09-1.png.png (left of Map11)
interactions += make_room_interactions("Map09-1.png.png", right=None, left=None, top="Map06-1.png.png", bottom=None)
# Map10-1.png.png (left of Map09)
interactions += make_room_interactions("Map10-1.png.png", right=None, left=None, top="Map07-1.png.png", bottom=None)
# Add bottom middle hitbox to Map09-1.png.png that requires items0, items2, and items5
interactions.append(
    Interaction(
        "Map09-1.png.png",
        WIDTH // 2.3, HEIGHT - 60, 100, 60,  # x, y, width, height (bottom middle)
        None,  # target_room (set to your desired room)
        WIDTH // 2, 80,  # target_x, target_y (set as needed)
        item0_required=True,
        item2_required=True,
        item5_required=True
    )
)

current_room = "background.png"  # Start room

# Background Actor setup
background = Actor(current_room, (WIDTH//2, HEIGHT//2))
background.width = WIDTH
background.height = HEIGHT

# Animation frame sets for Leon2
forward_frames = [f"leon final{i:02}.png" for i in range(0, 4)]      # Down (00-03)
backward_frames= [f"leon final{i:02}.png" for i in range(4, 8)]      # Up (04-07)
right_frames   = [f"leon final{i:02}.png" for i in range(8, 12)]     # Right (08-11)
left_frames    = [f"leon final{i:02}.png" for i in range(12, 16)]    # Left (12-15)

player = Actor(forward_frames[0], (WIDTH//2, HEIGHT//2))
player.scale = SCALE
current_frames = forward_frames
frame_index = 0
frame_timer = 0
frame_delay = 11 

# Game state variables
game_over = False
score = 0
lives = 3
interact_cooldown = 0  # Frames until next allowed interaction

# Axe setup (center of left room)
axe_img = "items7.png"
axe_pos = (WIDTH // 2, HEIGHT // 2)
axe = Actor(axe_img, axe_pos)
axe.scale = 2.5
axe_picked_up = False

# Axe bobbing variables
axe_bob_timer = 5
axe_bob_up = True
axe_base_y = axe.y

# Item1 setup (center of Map17 room)
item1_img = "items1.png"
item1_pos = (WIDTH // 2, HEIGHT // 2)
item1 = Actor(item1_img, item1_pos)
item1.scale = 2.5
item1_picked_up = False

# item3 setup (center of Map17 room)
item3_img = "items3.png"
item3_pos = (WIDTH // 2, HEIGHT // 2)
item3 = Actor(item3_img, item3_pos)
item3.scale = 2.5
item3_picked_up = False

# item2 setup (center of Map07 room)
item2_img = "items2.png"
item2_pos = (WIDTH // 2, HEIGHT // 2)
item2 = Actor(item2_img, item2_pos)
item2.scale = 2.5
item2_picked_up = False

# item6 setup (center of Map07 room)
item6_img = "items6.png"
item6_pos = (WIDTH // 2, HEIGHT // 2)
item6 = Actor(item6_img, item6_pos)
item6.scale = 2.5
item6_picked_up = False

# item5 setup (center of Map07 room)
item5_img = "items5.png"
item5_pos = (WIDTH // 2, HEIGHT // 2)
item5 = Actor(item5_img, item5_pos)
item5.scale = 2.5
item5_picked_up = False

# item0 setup (center of Map07 room)
item0_img = "items0.png"
item0_pos = (WIDTH // 2, HEIGHT // 2)
item0 = Actor(item0_img, item0_pos)
item0.scale = 2.5
item0_picked_up = False

# Give all items if dev tool is enabled (runs once at game start)
if give_all_items:
    axe_picked_up = True
    item1_picked_up = True
    item2_picked_up = True
    item3_picked_up = True
    item6_picked_up = True
    item5_picked_up = True
    item0_picked_up = True

# random number generator for random events that could occur
def random_number():
    return random.randint(1, 100)



def update():
    global score, lives, game_over, frame_index, frame_timer, current_frames, show_interact
    global show_placemat_interact, current_room, interact_cooldown, axe_picked_up, item2_picked_up
    global axe_bob_timer, axe_bob_up, axe_base_y, interact_message, item1_picked_up, item3_picked_up, item6_picked_up, item5_picked_up, item0_picked_up
    global final_room_mode, final_room_frame, final_room_timer
    if game_over:
        return
    if final_room_mode:
        # Only animate the final room
        final_room_timer += 1
        if final_room_timer >= final_room_frame_delay:
            final_room_frame = (final_room_frame + 1) % len(final_room_images)
            final_room_timer = 0
        return
    if interact_cooldown > 0:
        interact_cooldown -= 1
    moving = False
    show_interact = False
    show_placemat_interact = False
    interact_message = None
    speed = 2
    if test_speed_modifier:
        speed *= 4
    # Movement with map boundary checks
    if keyboard.w:
        if player.y - speed - (player.height * player.scale) // 2 >= -50:
            player.y -= speed
        current_frames = backward_frames
        moving = True
    elif keyboard.s:
        if player.y + speed + (player.height * player.scale) // 2 <= 700:
            player.y += speed
        current_frames = forward_frames
        moving = True
    elif keyboard.a:
        if player.x - speed - (player.width * player.scale) // 2 >= -100:
            player.x -= speed
        current_frames = left_frames
        moving = True
    elif keyboard.d:
        if player.x + speed + (player.width * player.scale) // 2 <= 900:
            player.x += speed
        current_frames = right_frames
        moving = True
    if moving:
        frame_timer += 1
        if frame_timer >= frame_delay:
            frame_index = (frame_index + 1) % len(current_frames)
            player.image = current_frames[frame_index]
            frame_timer = 0
    else:
        frame_index = 0
        player.image = current_frames[frame_index]
    # Interaction logic
    for interaction in interactions:
        if interaction.source_room == current_room:
            if interaction.is_on(player.x, player.y):
                # FINAL ROOM TRIGGER: Map09-1 bottom hitbox
                if (interaction.source_room == "Map09-1.png.png" and
                    interaction.item0_required and interaction.item2_required and interaction.item5_required):
                    if not (item0_picked_up and item2_picked_up and item5_picked_up):
                        show_placemat_interact = False
                        interact_message = "It seems this door is locked and requires the RED, YELLOW, and BLUE keys"
                        break
                    if keyboard.e and interact_cooldown == 0:
                        final_room_mode = True
                        final_room_frame = 0
                        final_room_timer = 0
                        interact_cooldown = 50
                        break
                # Special logic for Map15 left door
                if interaction.axe_required and not axe_picked_up:
                    show_placemat_interact = False
                    interact_message = "The door is broken, maybe I can break it down somehow"
                    break
                # Special logic for Map13 bottom door (item1)
                if getattr(interaction, 'item1_required', False) and not item1_picked_up:
                    show_placemat_interact = False
                    interact_message = "It seems the PURPLE door is locked"
                    break
                # Special logic for Map13 bottom door (item1)
                if getattr(interaction, 'item3_required', False) and not item3_picked_up:
                    show_placemat_interact = False
                    interact_message = "It seems the GREEN door is locked"
                    break
                if getattr(interaction, 'item2_required', False) and not item2_picked_up:
                    show_placemat_interact = False
                    interact_message = "It seems the BLUE door is locked"
                    break
                if getattr(interaction, 'item6_required', False) and not item6_picked_up:
                    show_placemat_interact = False
                    interact_message = "It seems the PINK door is locked"
                    break
                if getattr(interaction, 'item5_required', False) and not item5_picked_up:
                    show_placemat_interact = False
                    interact_message = "It seems the YELLOW door is locked"
                    break
                if getattr(interaction, 'item0_required', False) and not item0_picked_up:
                    show_placemat_interact = False
                    interact_message = "It seems this door is locked and requires the RED, YELLOW, and BLUE keys"
                    break
                show_placemat_interact = True
                if keyboard.e and interact_cooldown == 0:
                    player.x = interaction.target_x
                    player.y = interaction.target_y
                    current_room = interaction.target_room
                    interact_cooldown = 50
                    break
    # Axe auto-pickup logic (only in left room and if not already picked up)
    if current_room == "Map12-1.png.png" and not axe_picked_up:
        if (abs(player.x - axe.x) < (player.width * player.scale)//6 and
            abs(player.y - axe.y) < (player.height * player.scale)//6):
            axe_picked_up = True
            interact_cooldown = 10
    # Item1 auto-pickup logic (only in Map17 and if not already picked up)
    if current_room == "Map16-1.png.png" and not item1_picked_up:
        if (abs(player.x - item1.x) < (player.width * player.scale)//6 and
            abs(player.y - item1.y) < (player.height * player.scale)//6):
            item1_picked_up = True
            interact_cooldown = 10

    # Item3 auto-pickup logic (only in Map17 and if not already picked up)
    if current_room == "Map17-1.png.png" and not item3_picked_up:
        if (abs(player.x - item3.x) < (player.width * player.scale)//6 and
            abs(player.y - item3.y) < (player.height * player.scale)//6):
            item3_picked_up = True
            interact_cooldown = 10
    # Item2 auto-pickup logic (only in Map07 and if not already picked up)
    if current_room == "Map07-1.png.png" and not item2_picked_up:
        if (abs(player.x - item2.x) < (player.width * player.scale)//6 and
            abs(player.y - item2.y) < (player.height * player.scale)//6):
            item2_picked_up = True
            interact_cooldown = 10

    if current_room == "Map06-1.png.png" and not item6_picked_up:
        if (abs(player.x - item6.x) < (player.width * player.scale)//6 and
            abs(player.y - item6.y) < (player.height * player.scale)//6):
            item6_picked_up = True
            interact_cooldown = 10

    if current_room == "Map10-1.png.png" and not item5_picked_up:
        if (abs(player.x - item5.x) < (player.width * player.scale)//6 and
            abs(player.y - item5.y) < (player.height * player.scale)//6):
            item5_picked_up = True
            interact_cooldown = 10
            
    if current_room == "Map11-1.png.png" and not item0_picked_up:
        if (abs(player.x - item0.x) < (player.width * player.scale)//6 and
            abs(player.y - item0.y) < (player.height * player.scale)//6):
            item0_picked_up = True
            interact_cooldown = 10
    # Axe bobbing animation (only if not picked up and in left room)
    if current_room == "Map12-1.png.png" and not axe_picked_up:
        if axe_bob_up:
            axe.y = axe_base_y - 5
        else:
            axe.y = axe_base_y
        axe_bob_timer += 1
        if axe_bob_timer >= 15:
            axe_bob_up = not axe_bob_up
            axe_bob_timer = 0
    else:
        axe.y = axe_base_y

    # Item1 bobbing animation (only if not picked up and in Map17)
    if current_room == "Map16-1.png.png" and not item1_picked_up:
        item1.y = item1_pos[1] - 5 if (pygame.time.get_ticks() // 500) % 2 == 0 else item1_pos[1]
    else:
        item1.y = item1_pos[1]

    # Item3 bobbing animation (only if not picked up and in Map17)
    if current_room == "Map17-1.png.png" and not item3_picked_up:
        item3.y = item3_pos[1] - 5 if (pygame.time.get_ticks() // 500) % 2 == 0 else item3_pos[1]
    else:
        item3.y = item3_pos[1]

    if current_room == "Map07-1.png.png" and not item2_picked_up:
        item2.y = item2_pos[1] - 5 if (pygame.time.get_ticks() // 500) % 2 == 0 else item2_pos[1]
    else:
        item2.y = item2_pos[1]

    if current_room == "Map06-1.png.png" and not item6_picked_up:
        item6.y = item6_pos[1] - 5 if (pygame.time.get_ticks() // 500) % 2 == 0 else item6_pos[1]
    else:
        item6.y = item6_pos[1]

    if current_room == "Map10-1.png.png" and not item5_picked_up:
        item5.y = item5_pos[1] - 5 if (pygame.time.get_ticks() // 500) % 2 == 0 else item5_pos[1]
    else:
        item5.y = item5_pos[1]

    if current_room == "Map11-1.png.png" and not item0_picked_up:
        item0.y = item0_pos[1] - 5 if (pygame.time.get_ticks() // 500) % 2 == 0 else item0_pos[1]
    else:
        item0.y = item0_pos[1]

def draw():
    global last_hitbox_room
    screen.clear()
    if final_room_mode:
        # Draw the animated final room background, scaled to fit the window
        final_img = final_room_images[final_room_frame]
        img = pygame.image.load(f"images/{final_img}")
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        screen.surface.blit(img, (0, 0))
        return
    # Scale and draw the background to fit the window using pygame directly
    bg = pygame.image.load(f"images/{current_room}")
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))  # Always scale to window size
    screen.surface.blit(bg, (0, 0))
    # Draw interaction hitboxes if enabled
    if show_hitboxes:
        # Draw interaction hitboxes (full size)
        if last_hitbox_room != current_room:
            room_hitbox_cache.clear()
            for interaction in interactions:
                if interaction.source_room == current_room and interaction.show_hitbox:
                    hitbox_cache_key = (interaction.x, interaction.y, interaction.width, interaction.height)
                    size = (interaction.width, interaction.height)
                    if size not in hitbox_img_cache:
                        hitbox_img_cache[size] = pygame.transform.scale(hitbox_img_original, size)
                    room_hitbox_cache[hitbox_cache_key] = (hitbox_img_cache[size], interaction.x, interaction.y - interaction.height//2)
            last_hitbox_room = current_room
        for img, x, y in room_hitbox_cache.values():
            screen.surface.blit(img, (x, y))
        # Draw item hitboxes (smaller, 60% of sprite size)
        item_hitboxes = [
            (axe, axe_picked_up, "Map12-1.png.png"),
            (item1, item1_picked_up, "Map16-1.png.png"),
            (item3, item3_picked_up, "Map17-1.png.png"),
            (item2, item2_picked_up, "Map07-1.png.png"),
            (item6, item6_picked_up, "Map06-1.png.png"),
            (item5, item5_picked_up, "Map10-1.png.png"),
            (item0, item0_picked_up, "Map11-1.png.png"),
        ]
        for item, picked_up, room in item_hitboxes:
            if current_room == room and not picked_up:
                w = int(item.width * item.scale * 0.4)
                h = int(item.height * item.scale * 0.4)
                x = int(item.x - w//2)
                y = int(item.y - h//2)
                size = (w, h)
                if size not in hitbox_img_cache:
                    hitbox_img_cache[size] = pygame.transform.scale(hitbox_img_original, size)
                screen.surface.blit(hitbox_img_cache[size], (x, y))
        # Draw player hitbox (smaller, 60% of sprite size)
        w = int(player.width * player.scale * 0.2)
        h = int(player.height * player.scale * 0.3)
        x = int(player.x - w//2)
        y = int(player.y - h//2)
        size = (w, h)
        if size not in hitbox_img_cache:
            hitbox_img_cache[size] = pygame.transform.scale(hitbox_img_original, size)
        screen.surface.blit(hitbox_img_cache[size], (x, y))
    # Draw item1 if in Map17 and not picked up
    if current_room == "Map16-1.png.png" and not item1_picked_up:
        item1.draw()
    # Draw axe if in left room and not picked up
    if current_room == "Map12-1.png.png" and not axe_picked_up:
        axe.draw()

    if current_room == "Map17-1.png.png" and not item3_picked_up:
        item3.draw()
    
    if current_room == "Map07-1.png.png" and not item2_picked_up:
        item2.draw()

    if current_room == "Map06-1.png.png" and not item6_picked_up:
        item6.draw()

    if current_room == "Map10-1.png.png" and not item5_picked_up:
        item5.draw()

    if current_room == "Map11-1.png.png" and not item0_picked_up:
        item0.draw()
    
    # Draw player
    player.draw()
    # Draw axe in inventory if picked up (half size)
    if axe_picked_up:
        axe_inventory_x = WIDTH - 40
        axe_inventory_y = 40
        axe_inventory = Actor(axe_img, (axe_inventory_x, axe_inventory_y))
        axe_inventory.scale = SCALE / 2
        axe_inventory.draw()
    # Draw item1 in inventory if picked up (half size, offset)
    if item1_picked_up:
        item1_inventory_x = WIDTH - 80
        item1_inventory_y = 40
        item1_inventory = Actor(item1_img, (item1_inventory_x, item1_inventory_y))
        item1_inventory.scale = SCALE / 1.5
        item1_inventory.draw()
    # Draw item3 in inventory if picked up (half size, offset)
    if item3_picked_up:
        item3_inventory_x = WIDTH - 120
        item3_inventory_y = 40
        item3_inventory = Actor(item3_img, (item3_inventory_x, item3_inventory_y))
        item3_inventory.scale = SCALE / 1.5
        item3_inventory.draw()
    # Draw item2 in inventory if picked up (half size, offset)
    if item2_picked_up:
        item2_inventory_x = WIDTH - 160
        item2_inventory_y = 40
        item2_inventory = Actor(item2_img, (item2_inventory_x, item2_inventory_y))
        item2_inventory.scale = SCALE / 1.5
        item2_inventory.draw()
    # Draw item6 in inventory if picked up (half size, offset)
    if item6_picked_up:
        item6_inventory_x = WIDTH - 200
        item6_inventory_y = 40
        item6_inventory = Actor(item6_img, (item6_inventory_x, item6_inventory_y))
        item6_inventory.scale = SCALE / 1.5
        item6_inventory.draw()
    # Draw item5 in inventory if picked up (half size, offset)
    if item5_picked_up:
        item5_inventory_x = WIDTH - 240
        item5_inventory_y = 40
        item5_inventory = Actor(item5_img, (item5_inventory_x, item5_inventory_y))
        item5_inventory.scale = SCALE / 1.5
        item5_inventory.draw()
    # Draw item5 in inventory if picked up (half size, offset)
    if item0_picked_up:
        item0_inventory_x = WIDTH - 280
        item0_inventory_y = 40
        item0_inventory = Actor(item0_img, (item0_inventory_x, item0_inventory_y))
        item0_inventory.scale = SCALE / 1.5
        item0_inventory.draw()
    # Show interaction prompt for any interactable area
    if interact_message:
        screen.draw.text(interact_message, center=(WIDTH//2, HEIGHT-40), fontsize=32, color="white")
    elif show_placemat_interact:
        screen.draw.text("Press E to interact", center=(WIDTH//2, HEIGHT-40), fontsize=32, color="white")
    if game_over:
        screen.draw.text("Game Over", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="red")

pgzrun.go()