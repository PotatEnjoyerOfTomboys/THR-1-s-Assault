import pygame as pg
import os
import random


# Do a web version with pybag?

# Get it done in a year
# Music 7
# 	1 menu track            (smooth jazz)
# 	3 mission track (Like SMT3's normal battle theme, solos are different)
#       Industrial Park     ()
#       Red Desert          ()
#       Iron Mines          (The end is almost there)
# 	1 THR-1 boss track      ()
# 	1 Curtis boss theme	    (Confidant)
# 	1 final boss track      (SHIT IS ABOUT TO END!!!)

# Secret level?

# Unlock tree
# Second weapon choice      Character must be alive after beating a stage 5 boss
# Third weapon choice       Character must be alive after beating a stage 10 boss
# Zoar Colonists            Beat a stage 15 boss
# Encyclopedia entries
#   Enemies                 Finish missions (faction affects which are unlocked)
#       Grunt               Finish 3 mission against the faction
#       Shock               Finish 9 mission against the faction
#       Support             Finish 18 mission against the faction
#       Specialist 1        Finish 27 mission against the faction
#       Specialist 2        Finish 36 mission against the faction
#       Elite               Finish 45 mission against the faction
#       VIP                 Finish eliminate VIP
#   Bosses                  Beat the boss (Zoar Colonists and THR-1 have special boss entries)
#   Weapon                  When the weapon is unlocked
#   Mercenary group
#       Team info           When unlocking the group
#       Team members        When unlocking the group
#   Background info
#       Manufacturer        When a weapon they made is unlocked.
#       Enemy groups        Unlocked by default
#       Solar War           Unlocked by default (journalistic reports)
#       Events of NNTSS     Unlocked by default (presented in the form of rapports made by the Nest)

# TODO: fix enemy spawn in defense
# Version 1.0 - Final version
#   Upgrades
#       Colonist
#           Vivianne    8   (Need to code all tomboys)
#   Bosses
#       Armed Shield Generator  Tesla coil attack
#       Rigel                   (Final boss)

#       Fire Support Mech       Boost effects
#       THR-1 Boss fight        (Alt Final boss - Zoar route)   (Figure how to make it playable)
#       AA Site - Drone builder (animations)
#       Gilgamesh               (animations)

#   Versus mode
#       Balance changes (small ones)
#   Character conversations
#   Secret stage
#       Gonna be like L4D2. Small anomalies just rushing you
#   Encyclopedia
#   Animated weapons. Mostly for the pile bunker
#   Animated radio transmission portraits


# Cut
# 	Mission Modifiers
#       Unknown Forces  (Opposite player team spawn)


pg.mixer.pre_init()
pg.init()
pg.joystick.init()
WIN_WIDTH, WIN_HEIGHT = 630, 450
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = WIN_WIDTH, WIN_HEIGHT
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pg.RESIZABLE)
pg.display.set_icon(pg.image.load(os.path.join("Sprites/Icon.ico")))

CLOCK = pg.time.Clock()
pg.mixer.set_num_channels(32)


import Fun  # General use functions
import Items   # Everything crashes if I remove that
import Event
import Render
import Entity
import Upgrades
import Main_Loop


def main_game(party_info):
    big_game_loop = True
    current_mission = 1
    run_info = {
        "Player party": player_party,
        "Missions completed": 0,
        "Time spend in mission": 0,
        "Mission historic": [],  # {"Name": <str>, "Faction": <int>}

        # "Funds": 0,
        "Upgrades": [],
        "Funds": 10000000000, # "Upgrades": [i for i in Fun.UPGRADE_INFO],    # Used for testing
        "Available upgrades": [],
        "Upgrade pool": []
    }

    names = [name for name in party_info]
    for upgrade in Fun.UPGRADE_INFO:
        if Fun.UPGRADE_INFO[upgrade]["Tier"] != 1:
            continue
        if Fun.UPGRADE_INFO[upgrade]["Owner"] not in names and not Fun.UPGRADE_INFO[upgrade]["Owner"] == "Party":
            continue
        run_info["Upgrade pool"].append(upgrade)
    # run_info["Available upgrades"] = (
    Fun.update_available_upgrades(run_info)
    # add upgrades to the upgrade pool
    end_status = "Loss"
    # Meta game loop
    Fun.weapons_menu(WIN, CLOCK, party_info, run_info)
    while big_game_loop and current_mission <= 15:
        Fun.loading_screen(WIN, CLOCK)
        gaming = True
        load_level = True

        possible_levels = []
        # Check if it's a boss mission
        if current_mission in [5, 10]:
            boss_mission = [0, 1, 2]
            boss_mission.pop(Fun.get_random_element_from_list(boss_mission))
            for possible_level in boss_mission:
                l, ex = Fun.level_generator(possible_levels, party_info, run_info, current_mission=current_mission,
                                            faction=possible_level)
                possible_levels.append({"name": f"{possible_level}", "level": l, "extra info": ex})
        elif current_mission == 15:
            l, ex = Fun.level_generator(possible_levels, party_info, run_info, current_mission=current_mission)
            possible_levels.append({"name": f"{0}", "level": l, "extra info": ex})
        else:
            for possible_level in range(3):
                l, ex = Fun.level_generator(possible_levels, party_info, run_info, current_mission=current_mission,
                                            faction=possible_level)
                possible_levels.append({"name": f"{possible_level}", "level": l, "extra info": ex})

        # Add a menu to choose_weapons
        level, extra_info, party_info, out_party, give_up = Fun.mission_menu(WIN, CLOCK, possible_levels, party_info,
                                                                             run_info)
        if give_up:
            big_game_loop = False
            load_level = False
            # Fun.confirmation_popup(
            #         WIN, CLOCK, [350, 100],
            #         [
            #             {"Name": "OH SHIT", "Value": "Yes", "On select": "Return", "Render func": "Text only"}
            #         ],
            #     text="Game is about to crash out"
            # )
        if load_level:
            entities = {"entities": [], "items": [], "sounds": [], "bullets": [],
                        "background particles": [], "particles": [], "UI particles": [], "screen shake": [],
                        "cutscene stage": 0, "shadows": [], "scrolling": [], "scrolling target": []}

            scrolling_target_entities = []  # Use that
            # Load up the party
            player_count = 0
            for count, player_to_add in enumerate(out_party):
                name = player_to_add[0]
                input_method = player_to_add[1]
                info = party_info[name]["Info"].copy()

                # Check if the character drives the APC
                if player_to_add[2]:
                    apc_info = Entity.player_repertory[
                        {"THR-1": "Fortress", "Zoar Colonists": "Sand Buggy"}[player_party]
                    ].copy()
                    for i in [
                        "health", "armour", "damage resistances", "thickness", "vel max", "speed", "friction",
                        "dash", "weapon", "skills", "func input", "func act", "func draw", "on death",
                        "targeting range", "targeting angle", "stealth mod", "stealth counter", "wall hack",
                        "free var"
                    ]:
                        info[i] = apc_info[i]
                    info["name"] = "APC"

                # Add default outline
                info["free var"].update({"Outline": Fun.OUTLINE_TEAL})

                # Manage input functions, default is AI
                if input_method == "Keyboard & Mouse":
                    info["func input"] = Entity.player_input_keyboard
                    info["free var"].update({"Outline": Fun.PLAYER_OUTLINE_COLOUR[player_count]})

                    player_count += 1
                elif input_method in ["Controller 1", "Controller 2", "Controller 3", "Controller 4"]:
                    info["func input"] = {
                        "Controller 1": Entity.player_input_controller_1,
                        "Controller 2": Entity.player_input_controller_2,
                        "Controller 3": Entity.player_input_controller_3,
                        "Controller 4": Entity.player_input_controller_4
                    }[input_method]
                    info["Input mode"] = "Controller"
                    info["free var"].update({"Outline": Fun.PLAYER_OUTLINE_COLOUR[player_count]})
                    player_count += 1

                # Add players in
                entities["entities"].append(Entity.Entity(info))
                last_added_entity = entities["entities"][-1]
                if input_method != "COM":
                    scrolling_target_entities.append(last_added_entity)
                    last_added_entity.is_player = True

                # Handle spawn points
                if count > 0:
                    mc = entities["entities"][0]
                    last_added_entity.pos = Fun.random_point_in_circle(mc.pos, 16)
                    last_added_entity.free_var["Ally waypoint"] = mc
                else:
                    last_added_entity.pos = extra_info["Spawn"].copy()

                # Change health
                if not player_to_add[2]:
                    last_added_entity.health = party_info[last_added_entity.name]["Health"]
                # Apply upgrades
                # Go though all bought upgrades
                # print(last_added_entity)
                for character_upgrade in run_info["Upgrades"]:
                    # print(character_upgrade)
                    upgrade_info = Fun.UPGRADE_INFO[character_upgrade]
                    # Apply them if the character can use them.
                    if upgrade_info["Owner"] in ["Party", last_added_entity.name]:
                        last_added_entity.upgrades.append(
                            Upgrades.Upgrade(last_added_entity, Fun.UPGRADE_INFO[character_upgrade])
                        )

                # Reset the name to the correct one
                last_added_entity.name = name

            # Heal benched team members
            for team_member in party_info:
                member_benched = True
                for deployed_team_member in entities["entities"]:
                    if team_member == deployed_team_member.name:
                        member_benched = False
                        break
                if member_benched and (party_info[team_member]["Health"] > 0 or current_mission in [5, 10]):
                    party_info[team_member]["Health"] = Entity.player_repertory[team_member]["health"]

            # Load events
            new_events = []
            for events_to_load in level["events"]:
                event_name = events_to_load[0]
                event_trigger = Event.get_event_trigger(events_to_load[1])
                # event_functions = Event.get_event_function(events_to_load[3])
                event_functions = []
                for funcs in events_to_load[3]:
                    event_functions.append(getattr(Event, funcs))
                    # "Name", Event.relevant trigger, single use, Event.effects
                free_var = {}
                if len(events_to_load) == 5:
                    free_var = events_to_load[4]

                new_events.append(
                    Event.MissionEvent(event_name, event_trigger, events_to_load[2], event_functions,
                                       free_var=free_var))
            level["events"] = new_events

            # Spawn enemies
            for p in extra_info["Enemy spawns"]:
                Event.spawn_enemy(entities, p["Type"], Fun.random_point_in_circle(p["Pos"], 16), 360 * random.random())
                enemy = entities["entities"][-1]
                enemy.vel = Fun.move_with_vel_angle([0, 0], 6 + 2 * random.random(), enemy.angle)

            # Scrolling
            scrolling_target = Fun.find_scrolling_target(scrolling_target_entities)
            scrolling = scrolling_target
            entities["scrolling"] = scrolling
            # end_status = "Loss"
            # |Main game loop|------------------------------------------------------------------------------------------
            go_to_hub = False,  # mission_end_screen = False, True
            frame_2 = WIN.copy()
            Render.draw(WIN, CLOCK, 0, scrolling, scrolling_target, level, entities, 1)
            Fun.menu_transition_doom_screen_melt(WIN, CLOCK, WIN.copy(), frame_2)

            checked_time = False
            end_status, mission_end_screen, big_game_loop, party_info, time_spent = Main_Loop.main_loop(WIN, CLOCK, entities, level,
                                                                                            party_info, scrolling,
                                                                                            scrolling_target_entities)
            run_info["Time spend in mission"] += time_spent

            pg.mixer.music.fadeout(60)
            # |Mission end screen|----------------------------------------------------------------------------------
            if big_game_loop:
                # Save health to party info
                # For each member in the party
                deployed_team = []
                surviving_deployed_team = []
                for p in out_party:
                    deployed_team.append(p[0])
                    if p[2]:
                        surviving_deployed_team.append(p[0])
                        continue
                    # Assume death
                    party_info[p[0]]["Health"] = 0
                    # See if alive
                    for e in entities["entities"]:
                        if e.team == "Players":
                            # Add
                            # If Alive unmark death
                            if p[0] == e.name:
                                surviving_deployed_team.append(p[0])
                                party_info[e.name]["Health"] = e.health
                if end_status == "Win":
                    run_info["Funds"] += extra_info["Mission Reward"]
                    Fun.end_mission_menu(WIN, CLOCK, party_info, end_status)
                    run_info["Missions completed"] += 1
                    run_info["Mission historic"].append({
                        "Name": level["name"], "Mission": current_mission, "Faction": level["faction"],
                        "Deployed team": deployed_team, "Surviving deployed team": surviving_deployed_team
                    })
                    current_mission += 1
                if end_status == "Loss":
                    big_game_loop = False

        # Story stuff
        # Story Beat 1
        # THR-1
        # Zoar
        # Story Beat 2
        # THR-1
        # Zoar
        # Endings
        # THR-1 Good    THR-1 gets paid, but Emperor presses on Secretary to tell him what that mission was about. She mentions a project but that's it.
        # THR-1 Bad     Secretary says that they failed the mission, but she can still manage to salvage the situation. They don't get paid as much as promised.
        # Zoar Good     Curtis
        # Zoar Bad      Curtis
    # Run end screen
    Fun.end_run_menu(WIN, CLOCK, run_info, party_info, end_status)  # TODO: Fix inputs not working there
    # Unlock stuff here
    # Check through the run history
    save_data = Fun.get_from_json("Save.json", "Everything")
    unlocked_weapons = save_data["Character weapons unlocked"]
    for m in run_info["Mission historic"]:
        # {'Player party': 'THR-1', 'Missions completed': 0, 'Mission historic': [], 'Funds': 0, 'Upgrades': [], 'Available upgrades': []}
        if m["Mission"] == 5:
            for p in m["Surviving deployed team"]:
                if 1 not in unlocked_weapons[p]:
                    unlocked_weapons[p].append(1)
                    # Confirmation pop up
                    Fun.confirmation_popup(
                        WIN, CLOCK, [350, 100],
                        [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
                        text=f"New weapon unlocked - {Fun.weapon_ownership_table[p][1]}"
                    )
        if m["Mission"] == 10:
            for p in m["Surviving deployed team"]:
                if 2 not in unlocked_weapons[p]:
                    unlocked_weapons[p].append(2)
                    # Confirmation pop up
                    Fun.confirmation_popup(
                        WIN, CLOCK, [350, 100],
                        [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
                        text=f"New weapon unlocked - {Fun.weapon_ownership_table[p][2]}"
                    )


    save_data["Character weapons unlocked"] = unlocked_weapons
    Fun.dict_to_json("Save.json", save_data)


def versus_mode(party_info):
    while True:
        # Menus

        Fun.loading_screen(WIN, CLOCK)
        gaming = True
        load_level = True

        possible_levels = []
        for p in os.listdir(f'Maps/Versus mode'):
            if os.path.splitext(f'Maps/Versus mode/{p}')[1] in [".png"]:
                l, ex = Fun.versus_level_generator(possible_levels, party_info, p)
                possible_levels.append({"name": f"{p}", "level": l, "extra info": ex})

        # Modified mission selection menu to let choose between versus maps
        level, extra_info, party_info, out_party, give_up = Fun.versus_arena_menu(WIN, CLOCK, possible_levels, party_info)

        if give_up:
            return

        # Load level
        entities = {"entities": [], "items": [], "sounds": [], "bullets": [],
                    "background particles": [], "particles": [], "UI particles": [], "screen shake": [],
                    "cutscene stage": 0, "shadows": [], "scrolling": [], "scrolling target": []}

        scrolling_target_entities = []  # Use that
        # Load up the party
        player_count = 0
        for count, player_to_add in enumerate(out_party):
            name = player_to_add[0]
            input_method = player_to_add[1]
            info = party_info[name]["Info"].copy()

            # Manage input functions, default is AI
            if input_method == "Keyboard & Mouse":
                info["func input"] = Entity.player_input_keyboard

            elif input_method in ["Controller 1", "Controller 2", "Controller 3", "Controller 4"]:
                info["func input"] = {
                    "Controller 1": Entity.player_input_controller_1,
                    "Controller 2": Entity.player_input_controller_2,
                    "Controller 3": Entity.player_input_controller_3,
                    "Controller 4": Entity.player_input_controller_4
                }[input_method]
                info["Input mode"] = "Controller"

            # Change weapons
            info["weapon"] = player_to_add[2]

            # Add outline based on position number and players in
            info["free var"].update({"Outline": Fun.PLAYER_OUTLINE_COLOUR[player_count]})
            entities["entities"].append(Entity.Entity(info))
            last_added_entity = entities["entities"][-1]
            scrolling_target_entities.append(last_added_entity)

            player_count += 1
            last_added_entity.team = f"Player {player_count}"

            if input_method != "COM":
                # New AI for COM?
                last_added_entity.is_player = True

            # Handle spawn points
            num = random.randint(0, len(extra_info["Spawn"])-1)
            last_added_entity.pos = extra_info["Spawn"][num]
            extra_info["Spawn"].pop(num)

            # Reset the name to the correct one
            last_added_entity.name = name
            last_added_entity.ai_state = "Attack"
            last_added_entity.force_draw = True
            last_added_entity.max_health *= 5
            last_added_entity.health *= 5
            last_added_entity.max_armour *= 5
            last_added_entity.armour *= 5
            last_added_entity.armour *= 5
            last_added_entity.targeting_angle = 180
            last_added_entity.targeting_range = 1280

        # Load events
        new_events = []
        for events_to_load in level["events"]:
            event_name = events_to_load[0]
            event_trigger = Event.get_event_trigger(events_to_load[1])
            # event_functions = Event.get_event_function(events_to_load[3])
            event_functions = []
            for funcs in events_to_load[3]:
                event_functions.append(getattr(Event, funcs))
                # "Name", Event.relevant trigger, single use, Event.effects
            free_var = {}
            if len(events_to_load) == 5:
                free_var = events_to_load[4]

            new_events.append(
                Event.MissionEvent(event_name, event_trigger, events_to_load[2], event_functions,
                                   free_var=free_var))
        level["events"] = new_events

        # Scrolling
        scrolling_target = Fun.find_scrolling_target(scrolling_target_entities)
        scrolling = scrolling_target
        entities["scrolling"] = scrolling

        # |Main game loop|------------------------------------------------------------------------------------------
        go_to_hub = False,  # mission_end_screen = False, True

        frame_2 = WIN.copy()
        Render.draw(WIN, CLOCK, 0, scrolling, scrolling_target, level, entities, 1)
        Fun.menu_transition_doom_screen_melt(WIN, CLOCK, WIN.copy(), frame_2)

        checked_time = False
        end_status, mission_end_screen, big_game_loop, party_info, time_spent = Main_Loop.main_loop(WIN, CLOCK, entities, level,
                                                                                        party_info, scrolling,
                                                                                        scrolling_target_entities,
                                                                                        end_with_main_player=False)

        pg.mixer.music.fadeout(60)
        # |Mission end screen|----------------------------------------------------------------------------------
        if big_game_loop:
            Fun.versus_end_menu(WIN, CLOCK, party_info, end_status)


# for p in range(1000):
#     Fun.level_generator([], current_mission=1, mission_type="", faction=0)
#     print(p)

if __name__ == "__main__":
    # |Load controls and save|------------------------------------------------------------------------------------------
    try:
        Fun.get_from_json("Save.json", "Everything")
        # Convert data file if needed
    except FileNotFoundError:
        Fun.print_to_error_stream("Save.json not found, creating new one")
        Fun.dict_to_json("Save.json", Fun.EMPTY_SAVE_FILE)

    save_data =  Fun.get_from_json("Save.json", "Everything")
    # Load control
    try:
        controls = Fun.PseudoPlayer().control
        Fun.SYSTEM_CONTROLS = Fun.get_from_json("Key binds.json", "System")
    except FileNotFoundError:
        Fun.print_to_error_stream("Key binds.json not found, creating new one")
        Fun.dict_to_json("Key binds.json", Fun.DEFAULT_KEY_BINDS)
        controls = Fun.PseudoPlayer().control

    # Fun.sound_test(Fun.PseudoPlayer(), WIN, CLOCK)
    Fun.pygame_splash_screen(WIN, CLOCK)
    Fun.my_own_shit(WIN, CLOCK)
    # Fun.game_intro(WIN, CLOCK, controls, Fun.PseudoPlayer())
    Fun.title_screen(WIN, CLOCK, controls)

    while True:
        player_party = Fun.main_menu(WIN, CLOCK)
        create_char_party_info = lambda char_name: {
            "Name": char_name,
            "Health": Entity.player_repertory[char_name]["health"],
            "Death message": "",
            "Info": Entity.player_repertory[char_name].copy(),
        }

        party_info = {
            "THR-1": {
                "Lord": create_char_party_info("Lord"),
                "Emperor": create_char_party_info("Emperor"),
                "Wizard": create_char_party_info("Wizard"),
                "Sovereign": create_char_party_info("Sovereign"),
                "Duke":create_char_party_info("Duke"),
                "Jester": create_char_party_info("Jester"),
                "Condor": create_char_party_info("Condor"),
            },
            "Zoar Colonists": {
                "Curtis": create_char_party_info("Curtis"),
                "Lawrence": create_char_party_info("Lawrence"),
                "Vivianne": create_char_party_info("Vivianne"),
                "Mark": create_char_party_info("Mark"),
            },
            "Versus": {
                "Lord": create_char_party_info("Lord"),
                "Emperor": create_char_party_info("Emperor"),
                "Wizard": create_char_party_info("Wizard"),
                "Sovereign": create_char_party_info("Sovereign"),
                "Duke":create_char_party_info("Duke"),
                "Jester": create_char_party_info("Jester"),
                "Condor": create_char_party_info("Condor"),

                "Curtis": create_char_party_info("Curtis"),
                "Lawrence": create_char_party_info("Lawrence"),
                "Vivianne": create_char_party_info("Vivianne"),
                "Mark": create_char_party_info("Mark"),
            }
        }[player_party].copy()

        if player_party == "Versus":
            versus_mode(party_info)
        else:
            main_game(party_info)
        #
