from django.conf import settings
from django.contrib.auth import logout
from django.http import *

import time, random, bisect


BAD_STATUS_CODES = [400, 403, 404, 410, 500, 501, 503] #getattr(settings, 'SPITE_BAD_STATUS_CODES', )
SLOW_RANGE = (1,5)

BAD_STATUS_CHANCE = 10
SLOW_CHANCE = 40
BREAK_POST_CHANCE = 10
LOG_OUT_CHANCE = 1
TOTAL_CHANCE = 50
OUT_OF = 100

# taken from this dude
# http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/
class WeightedRandomGenerator(object):
    def __init__(self, weights):
        self.totals = []
        running_total = 0

        for w in weights:
            running_total += w
            self.totals.append(running_total)

    def next(self):
        rnd = random.random() * self.totals[-1]
        return bisect.bisect_right(self.totals, rnd)

    def __call__(self):
        return self.next()

lets_get_em_wrg = WeightedRandomGenerator([TOTAL_CHANCE-OUT_OF, OUT_OF])
bad_status_wrg = WeightedRandomGenerator([BAD_STATUS_CHANCE-OUT_OF, BAD_STATUS_CHANCE])
tarpit_wrg = WeightedRandomGenerator([SLOW_CHANCE-OUT_OF, SLOW_CHANCE])
break_post_wrg = WeightedRandomGenerator([BREAK_POST_CHANCE-OUT_OF, BREAK_POST_CHANCE])
logout_wrg = WeightedRandomGenerator([LOG_OUT_CHANCE-OUT_OF, LOG_OUT_CHANCE])

class Spite:
    def process_request(self, request):
        self.fuck_this_guy = lets_get_em_wrg()

        # look who lucked out
        if not self.fuck_this_guy:
            return None

        self.we_tarpit_them = tarpit_wrg()
        self.stop_error_time = bad_status_wrg()
        self.mess_with_the_post = break_post_wrg()
        self.log_them_out = logout_wrg()

        # first we slow them down
        if self.we_tarpit_them:
            time.sleep(random.randint(**SLOW_RANGE))

        # then maybe we return an error.  whoopsie!  we're working on the site bugs, we promise!
        if self.stop_error_time:
            return HttpResponse('', status=random.choice(BAD_STATUS_CODES))

        # to really break their spirit, we pop a random item off a POST
        if self.mess_with_the_post:
            if request.POST:
                request.POST._mutable = True
                request.POST.pop(random.choice(request.POST.keys()))
                request.POST._mutable = False

            # files too while we are at it
            if request.FILES:
                request.FILES._mutable = True
                request.FILES.pop(random.choice(request.FILES.keys()))
                request.FILES._mutable = False

        # hmm maybe you're not logged in? you're a stupid user, you!
        if self.log_them_out:
            if request.user.is_authenticated():
                logout(request)

        return None

    def process_response(self, request, response):
        # lets break some random html

        # who needs css styles?

        return response
