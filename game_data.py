class user():
    def __init__(self, name, sid):
        self.name = name
        self.sid = sid

class game_room():
    def __init__(self, host):
        self.active_users = {host}
        self.host = host
    
    def add_user(user):
        self.active_users.add(user)

    def has_user(sid):
        return len({user for user in self.active_users if user.sid == sid}) > 0

    def remove_user(sid):
        self.active_users = {user for user in self.active_users if user.sid != sid}
    
    def num_users():
        return len(self.active_users)

