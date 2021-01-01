from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Color
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.config import Config
from matplotlib import pyplot as plt
import random

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Window.size = (1024, 800)


class Ant(Widget):
    life_span = NumericProperty(0)
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel = ReferenceListProperty(vel_x, vel_y)
    food_x = NumericProperty(0)
    food_y = NumericProperty(0)

    x_modifier = None
    y_modifier = None
    owning_queen_alive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bump_timer = random.randint(45, 60)
        self.owning_queen = None
        self.food_pos = None
        self.queen_pos = None
        self.status = None
        self.gene = 0
        self.food = 30
        self.red = 0.5
        self.blue = 0.5
        self.green = 0.5
        self.life_span = self.generate_life_span()
        self.ant = Ellipse(size=(15, 15))
        Color(self.red, self.blue, self.green)
        self.ant_center = [self.ant.pos[0]+(self.ant.size[0]/2), self.ant.pos[1]+(self.ant.size[1]/2)]
        self.waypoint = self.generate_waypoint()

    def reset_ant_ownership(self):
        self.owning_queen = None

    def ant_color(self):
        with self.canvas:
            Color(self.owning_queen.red, self.owning_queen.blue, self.owning_queen.green)

    def generate_waypoint(self):
        self.random_x = random.randint(-50, Window.width - 30)
        self.random_y = random.randint(0, Window.height - 30)
        self.waypoint = [self.random_x, self.random_y]
        return self.waypoint

    def search(self):
        self.status = 'search'
        try:
            self.vel = (self.waypoint[0] - self.ant.pos[0]) / 50, (self.waypoint[1] - self.ant.pos[1]) / 50
            self.ant.pos = Vector(self.vel) + self.ant.pos
            if self.waypoint[0] - 10 <= self.ant.pos[0] <= self.waypoint[0] + 10 and self.waypoint[1] - 10 <= \
                    self.ant.pos[1] <= self.waypoint[1] + 10:
                self.generate_waypoint()
        except TypeError:
            pass
        self.check_food_collision()

    def generate_life_span(self):
        age = random.randint(250, 400)
        return age + (self.gene * 3)

    def communicate(self):
        pass

    def go_to_food(self):
        self.status = 'go_to_food'
        try:
            self.waypoint = self.food_pos
            self.vel = (self.waypoint[0] - self.queen.pos[0]) / 50, (self.waypoint[1] - self.queen.pos[1]) / 50
            self.queen.pos = Vector(self.vel) + self.queen.pos
        except TypeError:
            pass

        distance = Vector(self.ant.pos).distance(self.food_pos)
        if distance <= 5:
            self.food_pos = None
            self.status = 'search'

        self.check_food_collision()

    def food_localized(self):
        if self.food_pos[0] != 0 and self.food_pos[1] != 0:
            pass

    def return_food(self):
        if self.owning_queen != None and self.food >= 50:
            try:
                self.waypoint = self.owning_queen.marker.pos
                self.vel = (self.waypoint[0] - self.ant.pos[0]) / 50, (self.waypoint[1] - self.ant.pos[1]) / 50
                self.ant.pos = Vector(self.vel) + self.ant.pos

            except TypeError:
                pass
        else:
            self.status = 'search'

    def check_food_collision(self):
        for i in Game.food_list:
            distance = Vector(self.ant.pos).distance(i.food_source.pos)
            if distance <= i.random_size:
                if i.size[0] > 0:
                    self.food_pos = i.food_source.pos
                    self.eat(i)
                    self.collision = True
            else:
                self.status = 'search'
                self.collision = False

    def eat(self, i):
        self.status = 'eat'
        self.waypoint = i.food_source.pos
        self.vel = (self.waypoint[0] - self.ant.pos[0]) / 50, (self.waypoint[1] - self.ant.pos[1]) / 50
        i.random_size -= .4
        self.food += .5
        self.status = 'search'

    def check_status(self):
        self.food -= .01
        if self.status is None:
            self.status = 'search'
        elif self.status == 'search':
            self.search()
        elif self.status == 'go_to_food':
            self.go_to_food()
        elif self.status == 'eat':
            self.check_food_collision()
        elif self.status == 'return_food':
            self.return_food()
        elif self.status == 'bump':
            self.bump()
        if self.owning_queen_alive is False:
            self.canvas.remove(self.ant)

    def waypoint_modifier(self):
        x = random.randrange(-100, 100)
        return x

    def bump(self):
        self.status = 'bump'
        if self.bump_timer > 0:
            if self.x_modifier == None:
                self.x_modifier = self.waypoint_modifier()
                self.y_modifier = self.waypoint_modifier()
            self.red = self.red - 0.3
            self.blue = self.blue - 0.3
            self.green = self.green - 0.3
            self.vel = ((self.ant.pos[0] + self.x_modifier) - self.ant.pos[0]) / 50, ((self.ant.pos[1] + self.y_modifier) - self.ant.pos[1]) / 50
            self.ant.pos = Vector(self.vel) + self.ant.pos
            self.bump_timer -= 1
        elif self.bump_timer == 0:
            self.x_modifier = None
            self.red = self.red
            self.blue = self.blue
            self.green = self.green
            self.bump_timer = random.randint(45, 60)
            self.status = 'search'

class Queen(Widget):
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel = ReferenceListProperty(vel_x, vel_y)
    life_span = NumericProperty(0)
    food = 30
    status = None
    queen_alive = True
    id = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = random.randint(1, 100)
        self.eggs_list = []
        self.ants_list = []
        self.gene = 0
        self.waypoint = self.generate_waypoint()
        self.position = self.generate_waypoint()
        self.life_span = self.generate_life_span()
        self.red = self.generate_random() / 10
        self.blue = self.generate_random() / 10
        self.green = self.generate_random() / 10
        Color(self.red, self.blue, self.green)
        self.queen = Ellipse(size=(30, 30), pos=(self.position[0], self.position[1]))
        Color(self.red, self.blue, self.green)
        self.marker = Ellipse(size=(1, 1), pos=(self.queen.pos[0], self.queen.pos[1]))
        self.collision = False

    def generate_random(self):
        x = random.randrange(1, 10)
        return x

    def gene_mutation(self):
        x = random.randrange(-15, 15)
        self.gene = self.gene + x
        return self.gene

    def reset_ant_list(self):
        self.ants_list = []
        self.eggs_list = []

    def generate_waypoint(self):
        self.random_x = random.randint(0, Window.width - 30)
        self.random_y = random.randint(0, Window.height - 30)
        self.waypoint = [self.random_x, self.random_y]
        return self.waypoint

    def generate_life_span(self):
        age = random.randint(400, 500)
        return age + (self.gene * 3)

    def search(self):
        self.status = 'search'
        self.check_food_collision()
        self.vel = (self.waypoint[0] - self.queen.pos[0]) / 50, (self.waypoint[1] - self.queen.pos[1]) / 50
        self.queen.pos = Vector(self.vel) + self.queen.pos
        self.marker.pos = self.queen.pos[0] + (self.queen.size[0] / 2), self.queen.pos[1] + (self.queen.size[1] / 2)
        if self.waypoint[0] - 15 <= self.queen.pos[0] <= self.waypoint[0] + 15 and self.waypoint[1] - 15 <= \
                self.queen.pos[1] <= self.waypoint[1] + 15:
            self.generate_waypoint()

    def check_food_collision(self):
        for i in Game.food_list:
            distance = Vector(self.queen.pos).distance(i.food_source.pos)
            if distance <= i.random_size:
                if i.size[0] > 0:
                    self.eat(i)

    def eat(self, i):
        self.status = 'eat'
        self.waypoint = i.food_source.pos
        self.vel = (self.waypoint[0] - self.queen.pos[0]) / 50, (self.waypoint[1] - self.queen.pos[1]) / 50
        self.queen.pos = Vector(self.vel) + self.queen.pos
        i.random_size -= .4
        self.food += .5
        self.status = 'search'

    def check_status(self):
        self.food -= .01
        if self.status is None:
            self.status = 'search'
        elif self.status == 'search':
            self.search()
        elif self.status == 'eat':
            self.check_food_collision()
        elif self.status == 'lay_eggs':
            pass
        if self.food >= 100:
            self.status = 'lay_eggs'


class Egg(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Color(1, 1, 1)
        self.timer = random.randint(30, 45)
        self.egg = Ellipse(size=(10, 10))
        self.gene = 0
        self.queen_chance = None
        self.owning_queen = None

    def queen_or_ant(self):
        self.queen_chance = random.randint(1, 100)

    def reset_egg_ownership(self):
        self.owning_queen = None

class Food_Source(Widget):
    timer = random.randint(100, 150)
    random_size = NumericProperty(0)
    random_x = NumericProperty(0)
    random_y = NumericProperty(0)
    random_coordinates = ReferenceListProperty(random_x, random_y)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.generate_coordinates()
        Color(.102, .34, 0)
        self.food_source = Ellipse(size=(self.random_size, self.random_size), pos=(self.random_x, self.random_y))

    def entropy(self):
        if Game.time % 60 == 0:
            self.random_size -= .01
            self.food_source.size = (self.random_size, self.random_size)

    def generate_coordinates(self):
        self.random_size = random.randint(25, 40)
        self.random_x = random.randint(0, Window.width - self.random_size)
        self.random_y = random.randint(0, Window.height - self.random_size)


class Game(Widget):
    time_history = []
    ant_number_history = []
    queen_number_history = []
    avg_gene_value_history = []

    food_list = []
    queen_list = []
    egg = ObjectProperty(None)
    ant_counter = ObjectProperty(None)
    ant_number = NumericProperty(0)
    avg_gene_value = 0
    avg_gene_value_var = 0
    time = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ant_number = str(self.ant_number)
        self.avg_gene_value = str(self.avg_gene_value)
        with self.canvas:
            self.initial_queen = Queen()
            self.ant_counter = Label(text="Number of ants: {}".format(self.ant_number), font_size=20, pos=(60, 100),
                                     color=[1, .3, .5, 1])
            self.queen_counter = Label(text="Number of queens: {}".format(str(len(self.queen_list))), font_size=20, pos=(60, 120),
                                     color=[1, .3, .5, 1])
            self.avg_gene_value_label = Label(text="Avarage gene value: {}".format(self.avg_gene_value), font_size=20, pos=(80, 80),
                                     color=[1, .3, .5, 1])

        self.initial_queen.gene = 1
        self.queen_list.append(self.initial_queen)


    def gather_data(self):
        if self.time % 60 == 0:
            self.time_history.append(int(self.time/120))
            self.ant_number_history.append(self.ant_number)
            self.queen_number_history.append(len(self.queen_list))
            self.avg_gene_value_history.append(self.avg_gene_value)

    def count_ants(self):
        self.ant_number = 0
        for queen in self.queen_list:
            self.ant_number += len(queen.ants_list)
        return self.ant_number

    def avg_gene_value_fun(self):
        genes = []
        for queen in self.queen_list:
            genes.append(queen.gene)
        try:
            self.avg_gene_value = sum(genes) / len(genes)
        except ZeroDivisionError:
            pass
        return self.avg_gene_value

    def update(self, dt):
        self.time += 1

        for queen in self.queen_list:
            queen.check_status()
            if queen.status == 'lay_eggs':
                self.lay_eggs()
            for ant in queen.ants_list:
                ant.check_status()

        self.create_food()
        for i in self.food_list:
            i.entropy()
        self.check_for_death()
        self.check_for_ant_collision()
        self.ant_from_egg()
        self.feed_queen()
        self.check_queen_collision()
        self.count_ants()
        self.avg_gene_value_fun()
        self.ant_counter.text = "Number of ants: {}".format(self.ant_number)
        self.queen_counter.text = "Number of queens: {}".format(str(len(self.queen_list)))
        self.avg_gene_value_label.text = "Avarage gene value: {}".format(str(round(self.avg_gene_value, 2)))
        self.gather_data()

    def check_for_death(self):
        for i in self.food_list:
            if i.random_size < 20:
                self.canvas.remove(i.food_source)
                self.food_list.remove(i)

        for queen in self.queen_list:
            queen.life_span -= .05
            if queen.food <= 0 or queen.life_span <= 0:
                if len(queen.eggs_list) > 0:
                    for egg in queen.eggs_list:
                        self.canvas.remove(egg.egg)
                        queen.eggs_list.remove(egg)

                if len(queen.ants_list) > 0:
                    for ant in queen.ants_list:
                        self.canvas.remove(ant.ant)
                        queen.ants_list.remove(ant)

                if len(queen.eggs_list) == 0 and len(queen.ants_list) == 0:
                    self.canvas.remove(queen.marker)
                    self.canvas.remove(queen.queen)
                    self.queen_list.remove(queen)

            for i in queen.ants_list:
                i.food -= .005
                i.life_span -= .05
                if i.life_span <= 0 or i.food <= 0:
                    self.canvas.remove(i.ant)
                    queen.ants_list.remove(i)

    def create_food(self):
        if len(self.food_list) < 50:
            with self.canvas:
                self.new_food = Food_Source()
            self.food_list.append(self.new_food)

    def lay_eggs(self):
        for queen in self.queen_list:
            if queen.food >= 40 and queen.status == 'lay_eggs':
                with self.canvas:
                    self.egg = Egg()
                self.egg.owning_queen = queen
                self.egg.gene = queen.gene
                self.egg.queen_or_ant()
                self.egg.egg.pos = self.egg.owning_queen.queen.pos
                if id(queen) == id(self.egg.owning_queen):
                    queen.eggs_list.append(self.egg)
                queen.food -= (15 + (queen.gene/10))

    def ant_from_egg(self):
        chance = 97
        for queen in self.queen_list:
            for egg in queen.eggs_list:
                egg.timer -= .1
                if egg.timer <= 0:
                    if egg.queen_chance < chance:
                        with self.canvas:
                            self.ant = Ant()
                        self.ant.gene = egg.gene
                        self.ant.owning_queen = egg.owning_queen
                        queen.ants_list.append(self.ant)
                        self.ant.ant_color()
                        self.ant.ant.pos = egg.egg.pos
                        self.canvas.remove(egg.egg)
                        queen.eggs_list.remove(egg)

                    elif egg.queen_chance >= chance:
                        with self.canvas:
                            self.new_queen = Queen()
                        self.new_queen.reset_ant_list()
                        mutation = self.new_queen.gene_mutation()
                        self.new_queen.gene = egg.gene + int(mutation)
                        self.new_queen.queen.pos = egg.egg.pos
                        self.canvas.remove(egg.egg)
                        queen.eggs_list.remove(egg)
                        self.queen_list.append(self.new_queen)

                        #TEST
                        print("New queen ID: ", id(self.new_queen))
                        print("Gene value: ", self.new_queen.gene)
                    else:
                        pass
                else:
                    pass

    def feed_queen(self):
        for queen in self.queen_list:
            for i in queen.ants_list:
                if i.food >= 70:
                    i.queen_pos = i.owning_queen.pos
                    i.status = 'return_food'

    def check_queen_collision(self):
        for queen in self.queen_list:
            for i in queen.ants_list:
                if i.status == 'return_food':
                    distance = Vector(i.ant.pos).distance(queen.marker.pos)
                    if distance <= 25:
                        i.food -= 25
                        queen.food += 25
                        i.status = 'search'

    def check_for_ant_collision(self):
        all_ants = []

        for queen in self.queen_list:
            for ant in queen.ants_list:
                all_ants.append(ant)

        for i in all_ants:
            for y in all_ants:
                distance = Vector(i.ant.pos).distance(y.ant.pos)
                if distance <= 10 and i != y:
                    i.bump()
                    y.bump()
                else:
                    pass

class AntHill(App):
    game = None
    def build(self):
        self.game = Game()
        Clock.schedule_interval(self.game.update, 1.0 / 40.0)
        return self.game

    def on_stop(self):
            plt.plot(self.game.time_history, self.game.queen_number_history, 'b', label='Number of queens')
            plt.plot(self.game.time_history, self.game.ant_number_history, 'g', label='Number of ants')
            plt.plot(self.game.time_history, self.game.avg_gene_value_history, 'r', label='Avarage gene value')
            plt.xlabel('Time')
            plt.legend()
            plt.savefig('ant_plot.png')
            plt.show()

if __name__ == "__main__":
    app = AntHill()
    app.run()
