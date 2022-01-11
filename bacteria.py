import random
import os
import datetime
import math

import matplotlib.pyplot as plt

"""
The faster you move, the more energy you consume. Food drops randomly. Agents mutate randomly.
To reproduce, a specimen needs to reach max energy, the resulting 2 new specimens have half of its max energy.
"""

STEPS = 100

TIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
os.makedirs(f'./runs/{TIME}')
XLIM = [-5, 5]
YLIM = [-5, 5]
plt.xlim(XLIM)
plt.ylim(YLIM)
plt.gca().axes.set_aspect(1)

DROP_FOOD_EACH_N_STEPS = 30
FOOD_MIN_ENERGY = 10
FOOD_MAX_ENERGY = 100

BACTERIA_N = 10
MAX_START_SPEED = 5
SPEED_ENERGY_CONSUMPTION_MULT = 0.5  # How punishing it is to be too fast
BACTERIA_MAX_START_ENERGY = 100
MUTATION_CHANCE = 1
MUTATION_VARIANCE = 0.1

SAVE_IMAGE_EACH_N_STEPS = 1
INIT_EXPLR_RATE = 1
EXPLR_RATE_DECREASE = 0.9  # Multiply
MIN_EXPLR = 0.001


def randangle():
    return 2 * math.pi * random.random() * random.choice((-1, 1))

def drop():
    return random.uniform(XLIM[0], XLIM[1]), random.uniform(YLIM[0], YLIM[1])

food_sources = []
class Food:
    def __init__(self):
        self.x, self.y = drop()
        self.energy = random.randint(FOOD_MIN_ENERGY, FOOD_MAX_ENERGY)
        self.radius = self.energy / 20
        self.eating_b = []
        food_sources.append(self)


bacteria = []
death_list = []
class Bacterium:
    def __init__(self, x=None, y=None, speed=None, max_energy=None):
        if not x and not y:
            self.x, self.y = drop()
        else:
            self.x, self.y = x, y
        if speed is None and max_energy is None:
            self.speed = random.uniform(1, MAX_START_SPEED)
            self.max_energy = random.uniform(1, BACTERIA_MAX_START_ENERGY)
        else:
            self.speed = speed
            self.max_energy = max_energy
        self.energy = self.max_energy / 2
        self.eating = False
        self.food = None
        bacteria.append(self)

    def color(self):
        return min(self.speed / MAX_START_SPEED, 1), min(self.max_energy / BACTERIA_MAX_START_ENERGY, 1), 1

    def closest_food(self):
        """Find closest food and return its coords"""
        closest_dist = math.inf
        closest = None
        for food in food_sources:
            dist = ((food.x - self.x) ** 2 + (food.y - self.y) ** 2) ** 0.5
            if dist < closest_dist:
                closest_dist = dist
                closest = food
        return closest

    @staticmethod
    def mutation_calc(attr):
        """Does the attr mutate? By how much?"""
        if random.random() <= MUTATION_CHANCE:
            lower = attr * MUTATION_VARIANCE
            return random.uniform(attr-lower, attr+lower)
        else:
            return attr

    def reproduce(self):
        """Splitting in 2, both having energy = max_energy/2. The parent needs to have max energy to reproduce"""
        speed = self.mutation_calc(self.speed)
        max_energy = self.mutation_calc(self.max_energy)
        # Spawning close to the parent:
        new_b_x = self.x + random.uniform(-1, 1)
        new_b_y = self.y + random.uniform(-1, 1)
        Bacterium(new_b_x, new_b_y, speed, max_energy)

for _ in range(BACTERIA_N):
    Bacterium()

Food()
step = 1
reproduced = 0
died = 0
while True:
    # Drop food:
    if step % DROP_FOOD_EACH_N_STEPS == 0 or not food_sources:
        Food()

    # Draw:
    if step % SAVE_IMAGE_EACH_N_STEPS == 0:
        for f in food_sources:
            circle = plt.Circle((f.x, f.y), f.radius, color='y', alpha=f.energy / (f.radius * 20))
            plt.gca().add_patch(circle)
        for b in bacteria:
            plt.scatter(b.x, b.y, color=b.color(), marker='s')
            # print(bacterium.speed, bacterium.max_energy)

        plt.title(f'Step: {step}; Bacteria remaining: {len(bacteria)}')
        plt.savefig(f'./runs/{TIME}/{step}', bbox_inches='tight')
        plt.clf()
        plt.xlim(XLIM)
        plt.ylim(YLIM)
        plt.gca().axes.set_aspect(1)

    # Movement and eating:
    for b in bacteria:
        if not b.eating:
            f = b.closest_food()
            if f:
                dist = ((f.x - b.x)**2 + (f.y - b.y)**2)**0.5
                if dist > f.radius:  # Too far => move closer
                    # Calculating new coordinates
                    A = f.x - b.x
                    B = f.y - b.y
                    C = (A**2 + B**2)**0.5
                    dist_to_move = min(b.speed, C - f.radius)
                    x = A/C * dist_to_move
                    y = B/A * x
                    b.x += x
                    b.y += y

                    b.energy -= dist_to_move * b.speed * SPEED_ENERGY_CONSUMPTION_MULT
                    if b.energy <= 0:  # Out of energy => death sentence:
                        death_list.append(b)
                else:  # No need to move => eat
                    b.eating = True
                    b.food = f
                    f.eating_b.append(b)
        else:  # Eating
            f = b.food
            f.energy -= 1
            b.energy += 1
            if f.energy <= 0:
                for b_ in f.eating_b:
                    b_.eating = False
                    b_.food = None
                food_sources.remove(f)
            if b.energy >= b.max_energy:
                print(f'Reproduction! Step: {step}')
                b.reproduce()
                reproduced += 1

    # Death:
    for b in death_list:
        print(f'Death! Step: {step}')
        try:
            b.food.eating_b.remove(b)
        except AttributeError:
            pass
        bacteria.remove(b)
        died += 1
    death_list = []

    # Finishing the run:
    if step == STEPS:
        print()
        print('Survivors (speed, max energy):')
        b_speed_sum = 0
        b_max_energy_sum = 0
        b_n = 0
        for b in bacteria:
            b_speed_sum += b.speed
            b_max_energy_sum += b.max_energy
            b_n += 1
            print(round(b.speed, 2), round(b.max_energy, 2))
        print(f'Survivors mean speed: {round(b_speed_sum/b_n, 2)};', end=' ')
        print(f'Survivors mean max energy: {round(b_max_energy_sum/b_n, 2)}')
        print(f'Initial number: {BACTERIA_N}; Survived: {len(bacteria)}; Reproduced: {reproduced}; Died: {died}')
        break
    elif not bacteria:
        print()
        print("Everyone died!")
        print(f'Initial number: {BACTERIA_N}; Survived: {len(bacteria)}; Reproduced: {reproduced}; Died: {died}')
        break
    step += 1