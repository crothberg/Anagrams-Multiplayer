import random

letters = list( 'A' * 13 + 
                'B' * 3 +
                'C' * 3 +
                'D' * 6 +
                'E' * 18 +
                'F' * 3 +
                'G' * 4 +
                'H' * 3 +
                'I' * 12 +
                'J' * 2 +
                'K' * 2 +
                'L' * 5 +
                'M' * 3 +
                'N' * 8 +
                'O' * 11 +
                'P' * 3 +
                'Q' * 2 +
                'R' * 9 +
                'S' * 6 +
                'T' * 9 +
                'U' * 6 +
                'V' * 3 +
                'W' * 3 + 
                'X' * 2 +
                'Y' * 3 +
                'Z' * 2)
class game_room():
    def __init__(self, host, users=None, middle=[]):
        if users is not None:
            self.active_users = users
        else:
            self.active_users = {host : []}
        self.host = host
        self.middle = middle
    
    def add_user(self, user):
        self.active_users[user] = dict()

    def has_user(self, username):
        return username in self.active_users.keys()

    def remove_user(self, removing):
        self.active_users = {username : data for (username, data) in self.active_users.items() if username != removing}
        if removing == self.host and self.num_users() > 0:
            self.host = list(self.active_users)[0]
    
    def num_users(self):
        return len(self.active_users)

    def generate_game_state(self):
        return {'host' : self.host,
                'users' : self.active_users,
                'middle' : self.middle}

    def letters_already_flipped(self):
        ret = self.middle.copy()
        for user in self.active_users.items():
            for word in user[1]:
                ret = ret + list(word)
        return ret

    def letters_remaining(self):
        return list_subtraction(letters, self.letters_already_flipped())

    def flip_tile(self):
        possibilities = self.letters_remaining()
        if len(possibilities) == 0:
            return None
        new_tile = random.choice(possibilities)
        self.middle.append(new_tile)
        return new_tile

    def steal_word(self, user, word):
        #Steal from middle
        new_middle = list_subtraction(self.middle, list(word))
        if new_middle is None:
            return False
        else:
            self.middle = new_middle
            self.active_users[user].append(word)
            return True


def deserialize_game_room(game_state):
    return game_room(game_state['host'], game_state['users'], game_state['middle'])

def list_subtraction(list1, list2):
    ret = list1.copy()
    for letter in list2:
        try:
            ret.remove(letter)
        except ValueError:
            return None
