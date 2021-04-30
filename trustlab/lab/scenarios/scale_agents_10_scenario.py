
NAME = 'Scale Agents 10'

AGENTS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

OBSERVATIONS = [{'author': 'A',
  'before': [],
  'message': 'Redecentralization of the Web',
  'observation_id': 1,
  'receiver': 'B',
  'sender': 'A',
  'topic': 'Web Engineering'},
 {'author': 'A',
  'before': [1],
  'message': 'Web of Things',
  'observation_id': 2,
  'receiver': 'B',
  'sender': 'A',
  'topic': 'Web Engineering'},
 {'author': 'A',
  'before': [2],
  'message': 'Web Assembly',
  'observation_id': 3,
  'receiver': 'B',
  'sender': 'A',
  'topic': 'Web Engineering'},
 {'author': 'C',
  'before': [3],
  'message': 'Semantic Web and Linked Open Data',
  'observation_id': 4,
  'receiver': 'B',
  'sender': 'C',
  'topic': 'Web Engineering'},
 {'author': 'C',
  'before': [4],
  'message': 'Redecentralization of the Web',
  'observation_id': 5,
  'receiver': 'B',
  'sender': 'C',
  'topic': 'Web Engineering'},
 {'author': 'C',
  'before': [5],
  'message': 'Web-based learning',
  'observation_id': 6,
  'receiver': 'B',
  'sender': 'C',
  'topic': 'Web Engineering'}]

HISTORY = {'A': {'B': 1.0, 'C': 1.0, 'D': 1.0},
 'B': {'A': 0, 'C': 0, 'D': 1.0},
 'C': {'A': 1.0, 'B': 1.0, 'D': 1.0},
 'D': {'A': 1.0, 'B': 1.0, 'C': 1.0},
 'E': {},
 'F': {},
 'G': {},
 'H': {},
 'I': {},
 'J': {}}

TRUST_THRESHOLDS = {'cooperation': 0.5, 'forgivability': -0.5}

WEIGHTS = {'age': 1.0,
 'agreement': 1.0,
 'authority': 1.0,
 'direct experience': 1.0,
 'popularity': 1.0,
 'provenance': 1.0,
 'recency': 1.0,
 'recommendation': 1.0,
 'related resource': 1.0,
 'specificity': 1.0,
 'topic': 1.0}

METRICS_PER_AGENT = {'A': ['direct experience', 'popularity', 'recommendation'],
 'B': ['direct experience', 'popularity', 'recommendation'],
 'C': ['direct experience', 'popularity', 'recommendation'],
 'D': ['direct experience', 'popularity', 'recommendation'],
 'E': [],
 'F': [],
 'G': [],
 'H': [],
 'I': [],
 'J': []}

AUTHORITIES = {}

TOPICS = {}

DESCRIPTION = 'Scalability Test with agent upscaling for WI 2020'

