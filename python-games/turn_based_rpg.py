import random
import time
import os

# ─── Colours ───────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause(msg="Press Enter to continue..."):
    input(f"\n{YELLOW}{msg}{RESET}")

# ─── Health Bar ─────────────────────────────────────────────
def health_bar(current, maximum, length=20):
    filled = int((current / maximum) * length)
    filled = max(0, filled)
    bar = "█" * filled + "░" * (length - filled)
    pct = current / maximum
    colour = GREEN if pct > 0.5 else YELLOW if pct > 0.25 else RED
    return f"{colour}[{bar}]{RESET} {current}/{maximum}"

# ─── Header ─────────────────────────────────────────────────
def print_header(player, enemy):
    clear()
    print(f"{BOLD}{CYAN}{'═' * 45}{RESET}")
    print(f"{BOLD}{CYAN}           ⚔  RAMZ'S RPG BATTLE ⚔{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 45}{RESET}\n")

    print(f"  {BOLD}{WHITE}YOU{RESET}   {health_bar(player['hp'], player['max_hp'])}")
    print(f"        Potions: {'🧪' * player['potions'] or 'None'}\n")

    print(f"  {BOLD}{RED}{enemy['name']}{RESET}  {health_bar(enemy['hp'], enemy['max_hp'])}")
    print(f"\n{CYAN}{'─' * 45}{RESET}\n")

# ─── Typing effect ──────────────────────────────────────────
def typewrite(text, delay=0.03):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

# ─── Enemy roster ───────────────────────────────────────────
ENEMIES = [
    {"name": "Goblin",    "hp": 80,  "max_hp": 80,  "attack": (6,  12), "reward": 30},
    {"name": "Orc",       "hp": 120, "max_hp": 120, "attack": (10, 18), "reward": 50},
    {"name": "Dark Mage", "hp": 90,  "max_hp": 90,  "attack": (14, 22), "reward": 70},
    {"name": "Dragon",    "hp": 200, "max_hp": 200, "attack": (18, 30), "reward": 120},
]

# ─── Intro ──────────────────────────────────────────────────
def intro():
    clear()
    print(f"\n{BOLD}{CYAN}{'═' * 45}{RESET}")
    print(f"{BOLD}{CYAN}       ⚔  RAMZ'S RPG BATTLE ⚔{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 45}{RESET}\n")
    typewrite(f"{YELLOW}Welcome, warrior. Your quest begins now...{RESET}", 0.04)
    time.sleep(0.5)
    name = input(f"\n{WHITE}Enter your name: {RESET}").strip() or "Ramz"
    return name

# ─── Shop ───────────────────────────────────────────────────
def shop(player):
    clear()
    print(f"\n{BOLD}{YELLOW}🛒  SHOP  —  Gold: {player['gold']}{RESET}\n")
    print(f"  1. Buy Potion      (20 gold)  — +20 HP per use")
    print(f"  2. Upgrade Attack  (40 gold)  — +3 to your max damage")
    print(f"  3. Leave shop\n")

    while True:
        choice = input(f"{WHITE}> {RESET}").strip()
        if choice == "1":
            if player["gold"] >= 20:
                player["potions"] += 1
                player["gold"] -= 20
                typewrite(f"{GREEN}You bought a potion! ({player['potions']} total){RESET}")
            else:
                typewrite(f"{RED}Not enough gold!{RESET}")
        elif choice == "2":
            if player["gold"] >= 40:
                player["attack"] = (player["attack"][0], player["attack"][1] + 3)
                player["gold"] -= 40
                typewrite(f"{GREEN}Attack upgraded! Max damage now {player['attack'][1]}{RESET}")
            else:
                typewrite(f"{RED}Not enough gold!{RESET}")
        elif choice == "3":
            break
        else:
            print("Pick 1, 2 or 3.")

# ─── Battle ─────────────────────────────────────────────────
def battle(player, enemy):
    typewrite(f"\n{RED}A {enemy['name']} appears!{RESET}", 0.04)
    time.sleep(0.6)

    while player["hp"] > 0 and enemy["hp"] > 0:
        print_header(player, enemy)

        print(f"  {BOLD}1.{RESET} ⚔  Attack")
        print(f"  {BOLD}2.{RESET} 🧪  Use Potion  ({player['potions']} left)")
        print(f"  {BOLD}3.{RESET} 🏃  Flee\n")

        choice = input(f"{WHITE}> {RESET}").strip()

        # ── Player turn ──────────────────────────────────
        if choice == "1":
            dmg = random.randint(*player["attack"])
            crit = random.random() < 0.15          # 15% crit chance
            if crit:
                dmg = int(dmg * 1.5)
                typewrite(f"{YELLOW}💥 CRITICAL HIT! You deal {dmg} damage!{RESET}")
            else:
                typewrite(f"{GREEN}You deal {dmg} damage.{RESET}")
            enemy["hp"] = max(0, enemy["hp"] - dmg)

        elif choice == "2":
            if player["potions"] > 0:
                heal = random.randint(20, 35)
                player["hp"] = min(player["max_hp"], player["hp"] + heal)
                player["potions"] -= 1
                typewrite(f"{GREEN}You drink a potion and heal {heal} HP.{RESET}")
            else:
                typewrite(f"{RED}No potions left!{RESET}")
                continue

        elif choice == "3":
            if random.random() < 0.5:
                typewrite(f"{YELLOW}You fled successfully!{RESET}")
                return "fled"
            else:
                typewrite(f"{RED}You couldn't escape!{RESET}")

        else:
            typewrite(f"{RED}Invalid choice — pick 1, 2 or 3.{RESET}")
            continue

        # ── Enemy turn ───────────────────────────────────
        if enemy["hp"] > 0:
            e_dmg = random.randint(*enemy["attack"])
            player["hp"] = max(0, player["hp"] - e_dmg)
            typewrite(f"{RED}{enemy['name']} hits you for {e_dmg} damage!{RESET}")

        time.sleep(0.5)

    if player["hp"] <= 0:
        return "lost"
    return "won"

# ─── Main ────────────────────────────────────────────────────
def main():
    name = intro()

    player = {
        "name":   name,
        "hp":     100,
        "max_hp": 100,
        "attack": (10, 20),
        "potions": 3,
        "gold":   0,
        "wins":   0,
    }

    for i, enemy_template in enumerate(ENEMIES):
        # Shop before every fight (except the first)
        if i > 0:
            typewrite(f"\n{YELLOW}You have {player['gold']} gold. Visit the shop?{RESET}")
            if input("(y/n) > ").strip().lower() == "y":
                shop(player)

        # Fresh copy of the enemy so HP resets each run
        enemy = dict(enemy_template)

        typewrite(f"\n{CYAN}⚔  Battle {i + 1}: {enemy['name']}{RESET}", 0.04)
        pause("Press Enter to fight...")

        result = battle(player, enemy)

        if result == "won":
            player["wins"] += 1
            player["gold"] += enemy["reward"]
            typewrite(f"\n{GREEN}Victory! You earned {enemy['reward']} gold.{RESET}", 0.04)
            # Small HP regen between fights
            regen = 20
            player["hp"] = min(player["max_hp"], player["hp"] + regen)
            typewrite(f"{GREEN}You rest and recover {regen} HP.{RESET}")
            pause()

        elif result == "lost":
            clear()
            print(f"\n{BOLD}{RED}{'═' * 45}{RESET}")
            typewrite(f"{RED}  💀  You were defeated by the {enemy['name']}...{RESET}", 0.04)
            print(f"{BOLD}{RED}{'═' * 45}{RESET}")
            typewrite(f"\n  Battles won: {player['wins']} / {len(ENEMIES)}")
            typewrite(f"  Gold earned: {player['gold']}")
            pause("Press Enter to exit.")
            return

        elif result == "fled":
            typewrite(f"{YELLOW}You live to fight another day...{RESET}")
            pause()
            # Fleeing skips that enemy — loop continues

    # Beat all enemies
    clear()
    print(f"\n{BOLD}{YELLOW}{'═' * 45}{RESET}")
    typewrite(f"{YELLOW}  🏆  YOU CONQUERED ALL ENEMIES, {name.upper()}!{RESET}", 0.04)
    print(f"{BOLD}{YELLOW}{'═' * 45}{RESET}")
    typewrite(f"\n  Final HP:  {player['hp']} / {player['max_hp']}")
    typewrite(f"  Gold:      {player['gold']}")
    typewrite(f"  Potions:   {player['potions']}")
    pause("Press Enter to exit.")

main()