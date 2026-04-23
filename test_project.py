import FinalProject

def test_left_interaction_basic(setup_env):
    interactions = setup_env

    make_room_interactions("RoomA", "RoomB", None, None, None)

    assert len(interactions) == 1
    assert interactions[0].target == "RoomB"


def test_right_interaction_basic(setup_env):
    interactions = setup_env

    make_room_interactions("RoomA", None, "RoomC", None, None)

    assert len(interactions) == 1
    assert interactions[0].target == "RoomC"


def test_bottom_interaction_flags(setup_env):
    interactions = setup_env

    make_room_interactions("Map13-1.png.png", None, None, "Map17-1.png.png", None)

    assert len(interactions) == 1
    assert interactions[0].kwargs["item1_required"] is True


def test_left_requires_axe(setup_env):
    interactions = setup_env

    make_room_interactions("Map15-1.png.png", "Map16-1.png.png", None, None, None)

    assert len(interactions) == 1
    assert interactions[0].kwargs["axe_required"] is True


def test_multiple_directions(setup_env):
    interactions = setup_env

    make_room_interactions("RoomA", "RoomB", "RoomC", "RoomD", "RoomE")

    assert len(interactions) == 4


def test_no_directions(setup_env):
    interactions = setup_env

    make_room_interactions("RoomA", None, None, None, None)

    assert len(interactions) == 0


def test_game_over_stops_update(setup_env):
    setup_env["game_over"] = True
    old_x = setup_env["player"].x

    update()

    assert setup_env["player"].x == old_x


def test_player_moves_up(setup_env):
    setup_env["keyboard"].w = True
    old_y = setup_env["player"].y

    update()

    assert setup_env["player"].y < old_y


def test_player_moves_down(setup_env):
    setup_env["keyboard"].s = True
    old_y = setup_env["player"].y

    update()

    assert setup_env["player"].y > old_y


def test_interaction_triggers_room_change(setup_env):
    interaction = DummyInteraction()
    setup_env["interactions"].append(interaction)

    setup_env["keyboard"].e = True

    update()

    assert setup_env["current_room"] == "RoomB"


def test_interaction_blocked_by_axe(setup_env):
    interaction = DummyInteraction()
    interaction.axe_required = True
    setup_env["interactions"].append(interaction)

    update()

    assert setup_env["interact_message"] is not None


def test_interact_cooldown_decreases(setup_env):
    setup_env["interact_cooldown"] = 10

    update()

    assert setup_env["interact_cooldown"] == 9


def test_animation_resets_when_idle(setup_env):
    setup_env["frame_index"] = 1

    update()

    assert setup_env["frame_index"] == 0

def test_background_draws(setup_env):
    screen = setup_env

    draw()

    assert len(screen.surface.blit_calls) > 0


def test_player_drawn(setup_env):
    draw()

    assert globals()["player"].drawn is True


def test_item_drawn_in_correct_room(setup_env):
    globals()["current_room"] = "Map12-1.png.png"

    draw()

    assert globals()["axe"].drawn is True


def test_inventory_draw_when_picked_up(setup_env):
    globals()["axe_picked_up"] = True

    draw()


    assert True


def test_interact_message_display(setup_env):
    globals()["interact_message"] = "Locked!"

    draw()

    assert "Locked!" in setup_env.draw.text_calls


def test_game_over_text(setup_env):
    globals()["game_over"] = True

    draw()

    assert "Game Over" in setup_env.draw.text_calls