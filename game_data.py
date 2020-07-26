class game_room():
    def __init__(self, host, users=None, center=[]):
        if users is not None:
            self.active_users = users
        else:
            self.active_users = [host]
        self.host = host
        self.center = center
    
    def add_user(self, user):
        self.active_users.add(user)

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
                'center' : self.center}

def deserialize_game_room(game_state):
    return game_room(game_state['host'], game_state['users'], game_state['center'])
