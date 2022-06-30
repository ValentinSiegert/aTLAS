import math
import pprint
import random
import string
import uuid
from datetime import datetime

context_levels = ['relaxed', 'important', 'critical']
max_seconds_time_delay = 63072000
max_lifetime_delay = 31536000

factors = [
    'content_trust.bias',
    'content_trust.specificity',
    'content_trust.likelihood',
    'content_trust.incentive',
    'content_trust.deception',
    'content_trust.age',
    'content_trust.authority',
    'content_trust.topic',
    'content_trust.provenance',
    'content_trust.direct_experience',
    'content_trust.recommendation',
    'content_trust.related_resources',
    'content_trust.user_expertise',
    'content_trust.popularity',
]

scales = {
    'marsh_briggs': {
        'cooperation': 0.5,
        'default': 0.0,
        'forgivability': -0.5,
        'maximum': 1.0,
        'minimum': -1.0,
        'name': 'Trust Scale by Marsh and Briggs (2009)',
        'package': 'marsh_briggs_scale'
    }
}


class Scenario(object):
    def __init__(self, observations, agents, file) -> None:
        super().__init__()
        # contraints
        self.n_observations = observations
        self.n_agents = agents

        # output handles
        self.output_file_name = file
        self.output_file_handle = open(file, 'w+')

        # data
        self.agents = []
        self.__topics__ = []
        self.__uris__ = []

    def generate_and_write_to_file(self):
        # pre-generate internal data
        self.__uris__ = [str(uuid.uuid4()) for _ in range(self.n_observations)]
        self.generate_agent_names(self.n_agents)
        self.generate_topics(self.n_observations)

        # add metadata to scenario file
        self.write_named_object_to_output(
            'NAME', f'Random_{self.n_agents}A-{self.n_observations}O_{int(round(random.random(), 6) * 1e6)}')
        self.write_named_object_to_output(
            'DESCRIPTION', f'Randomly generated scenario with {self.n_agents} agents and {self.n_observations} observations')
        self.write_named_object_to_output('AGENTS', self.agents)

        # observations
        self.generate_observations(self.n_observations, self.n_agents)

        # history
        self.generate_history()

        # scales
        self.generate_scales_per_agent()

        # metrics
        self.generate_metrics_per_agent()

    def write_string_to_output(self, str):
        self.output_file_handle.write(str)

    def write_named_object_to_output(self, name, obj):
        self.output_file_handle.write(f'{name} = {pprint.pformat(obj)}\n\n')

    def generate_agent_names(self, agents):
        for i in range(agents):
            self.agents.append(get_letter_code(i))

    def generate_topics(self, observations, max_length=20):
        letters = string.ascii_letters
        for _ in range(math.ceil(observations * (1 + random.random()))):
            self.__topics__.append(''.join(random.choice(letters)
                                   for i in range(random.randint(1, max_length))))

    def generate_observations(self, observations, agents_count):
        self.write_string_to_output('OBSERVATIONS = [')

        for i in range(observations):
            observation = {'observation_id': i,
                           'authors': random.sample(self.agents, random.randint(1, min(agents_count, 5))),
                           'before': [i - 1] if i > 0 else [], 'message': generate_message(),
                           'receiver': random.choice(self.agents), 'sender': random.choice(self.agents)}
            # avoid cases where sender equals receiver
            while observation['sender'] == observation['receiver']:
                observation['sender'] = random.choice(self.agents)
            # details
            observation['details'] = {
                'uri': self.__uris__[i],
                'content_trust.context_level': random.choice(context_levels),
                'content_trust.bias': random.random() * 2 - 1,
                'content_trust.deception': random.random() * 2 - 1,
                'content_trust.incentive': random.random() * 2 - 1,
                'content_trust.likelihood': random.random() * 2 - 1,
                'content_trust.specificity': random.random() * 2 - 1,
                'content_trust.topics': random.sample(self.__topics__, random.randint(1, min(len(self.__topics__), 5))),
                'content_trust.related_resources': random.sample(self.__uris__,
                                                                 random.randint(0, min(len(self.__uris__), 10))),
                'content_trust.publication_date': datetime.now().timestamp() - (max_seconds_time_delay *
                                                                                random.random())
            }

            self.write_string_to_output(pprint.pformat(observation))

            # if last object isn't reached, add comma and newline
            if i < observations - 1:
                self.write_string_to_output(',\n')

        self.write_string_to_output(']\n\n')

    def generate_history(self):
        self.write_string_to_output('HISTORY = {')

        for i, agent in enumerate(self.agents):
            agent_history = []
            for other_agent in self.agents:
                if other_agent != agent:
                    agent_history.append((other_agent, random.choice(
                        self.__uris__), random.random() * 2 - 1))

            if len(agent_history) > 0:
                # even if i is smaller than len(self.agents), the randomness might prevent another entry
                # -> add comma and newline here to prevent commas before empty lines
                str = ',\n' if i > 0 else ''
                str += f'{pprint.pformat(agent)}: {pprint.pformat(agent_history)}'
                self.write_string_to_output(str)

        self.write_string_to_output('}\n\n')

    def generate_scales_per_agent(self):
        self.write_string_to_output('SCALES_PER_AGENT = {')

        for i, agent in enumerate(self.agents):
            str = ',\n' if i > 0 else ''
            str += f'{pprint.pformat(agent)}: {pprint.pformat(scales["marsh_briggs"])}'
            self.write_string_to_output(str)

        self.write_string_to_output('}\n\n')

    def generate_metrics_per_agent(self):
        self.write_string_to_output('METRICS_PER_AGENT = {')

        for i, agent in enumerate(self.agents):
            thresholds = sorted([random.random() for _ in range(3)])
            # generate trusted topics
            trusted_topics = {}
            for other_agent in random.sample(self.agents, random.randint(0, len(self.agents))):
                agent_dict = {}
                for topic in random.sample(self.__topics__, random.randint(1, len(self.__topics__))):
                    agent_dict[topic] = random.random() * 2 - 1
                trusted_topics[other_agent] = agent_dict
            # generate weights
            weights = {}
            for factor in factors:
                weights[factor] = random.random()
            prefs = {
                '__final__': {
                    'name': 'weighted_average',
                    'weights': weights
                },
                'content_trust.age_grace_period_seconds': random.random() * 5260000,  # 2 months * random
                'content_trust.authority': random.sample(self.agents, random.randint(0, len(self.agents))),
                'content_trust.context_values': {'critical': thresholds[2], 'important': thresholds[1],
                                                 'relaxed': thresholds[0]},
                'content_trust.deception': random.random() - 1,
                'content_trust.direct_experience': {},
                'content_trust.max_lifetime_seconds': datetime.now().timestamp() - max_lifetime_delay * random.random(),
                'content_trust.popularity': {'peers': random.sample(self.agents, random.randint(1, len(self.agents)))},
                'content_trust.provenance': random.sample(self.agents, random.randint(0, len(self.agents))),
                'content_trust.recency_age_limit': datetime.now().timestamp() - max_lifetime_delay * random.random(),
                'content_trust.recommendation': {},
                'content_trust.related_resources': {},
                'content_trust.topic': trusted_topics,
                'content_trust.user_expertise': {}
            }
            # add enforce lifetime
            if random.random() < 0.3:
                prefs['content_trust.enforce_lifetime'] = {}

            str = ',\n' if i > 0 else ''
            str += f"{pprint.pformat(agent)}: {pprint.pformat(prefs)}"
            self.write_string_to_output(str)

        self.write_string_to_output('}\n\n')


def add_to_file_string(name, object2add, file_string='\n'):
    return file_string + f'{name} = {pprint.pformat(object2add)}\n\n'


def generate_message(max_length=50):
    letters = string.ascii_lowercase + ' '
    return ''.join(random.choice(letters) for i in range(random.randint(1, max_length)))


def get_letter_code(n, letters=string.ascii_uppercase):
    if n == 0:
        return letters[0]

    result = ''
    base = len(letters)
    while n > 0:
        q = n // base
        r = n % base
        result = letters[r] + result

        n = q

    return result
