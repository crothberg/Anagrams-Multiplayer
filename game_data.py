import random
import app
import time

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
    def __init__(self, host, users=None, middle=[], prev_source=[], challenge = None):
        if users is not None:
            self.active_users = users
        else:
            self.active_users = {host : []}
        self.host = host
        self.middle = middle
        self.prev_source = prev_source
        self.challenge = challenge
    
    def add_user(self, user):
        self.active_users[user] = []

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
                'middle' : self.middle,
                'prev_source' : self.prev_source,
                'challenge' : self.challenge}

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
        #Steal from person
        for username, words in self.active_users.items():
            for stealable_word in words:
                still_needed = list_subtraction(list(word), list(stealable_word))
                if still_needed is None:
                    continue
                new_middle = list_subtraction(self.middle, still_needed)
                if new_middle is None:
                    continue
                self.middle = new_middle
                self.active_users[user].append(word)
                self.active_users[username].remove(stealable_word)
                self.prev_source.append((user, word, list(still_needed), {username : stealable_word}))
                return True

        #Steal from middle
        new_middle = list_subtraction(self.middle, list(word))
        if len(word) < 3 or new_middle is None:
            return False
        else:
            self.middle = new_middle
            self.active_users[user].append(word)
            self.prev_source.append((user, word, list(word), dict()))
            return True

    def last_op(self):
        if len(self.prev_source) < 1:
            return None
        else:
            return self.prev_source[-1]

    def create_challenge(self):
        if self.challenge is not None or self.last_op() is None:
            return
        start_time = time.time()
        votes = {username : 0 for username in self.active_users}
        self.challenge = (start_time, votes)

    def set_vote(self, user, vote):
        if self.challenge is None:
            return
        vote_score = 0
        if vote = 'accept'
            vote_score = 1
        else:
            vote_score = -1
        self.challenge[1][user] = vote_score

    def all_votes_in(self):
        if self.challenge is None:
            return False
        votes_needed = [vote for uname, vote in self.challenge.items() if vote == 0]
        return len(votes_needed) < 1

    def finish_challenge(self):
        all_votes = [vote for uname, vote in self.challenge.items()]
        self.challenge = None
        if sum(all_votes) > 0:
            self.rollback()
            return True
        else:
            return False

    def rollback(self):
        last_op = self.last_op()
        if last_op is None:
            return
        self.middle = self.middle + last_op[2]
        self.active_users[last_op[0]].remove(last_op[1])
        for username, word in last_op[3].items():
            self.active_users[username].append(word)
        self.prev_source = self.prev_source[:-1]


def deserialize_game_room(game_state):
    return game_room(game_state['host'], game_state['users'], game_state['middle'], game_state['prev_source'], game_state['challenge'])

def list_subtraction(list1, list2):
    ret = list1.copy()
    for letter in list2:
        try:
            ret.remove(letter)
        except ValueError:
            #app.print_log_line('subtraction failed: "%s" from "%s"' % (list1.join(','), list2.join(',')))
            return None
    return ret
