import random

letters = list('abcdefghijklmnopqrstuvwxyz')
class game_room():
    def __init__(self, host, users=None, middle=[]):
        if users is not None:
            self.active_users = users
        else:
            self.active_users = [host]
        self.host = host
        self.middle = middle
    
    def add_user(self, user):
        self.active_users.append(user)

    def has_user(self, username):
        return username in self.active_users

    def remove_user(self, removing):
        self.active_users = [user for user in self.active_users if user != removing]
        if removing == self.host and self.num_users() > 0:
            self.host = self.active_users[0]
    
    def num_users(self):
        return len(self.active_users)

    def generate_game_state(self):
        return {'host' : self.host,
                'users' : self.active_users,
                'middle' : self.middle}

    def letters_already_flipped(self):
        return self.middle

    def letters_remaining(self):
        current_letters = letters.copy()
        for letter in self.letters_already_flipped():
            current_letters.remove(letter)
        return current_letters

    def flip_tile(self):
        possibilities = self.letters_remaining()
        if len(possibilities) == 0:
            return None
        new_tile = random.choice(possibilities)
        self.middle.append(new_tile)
        return new_tile


def deserialize_game_room(game_state):
    return game_room(game_state['host'], game_state['users'], game_state['middle'])
