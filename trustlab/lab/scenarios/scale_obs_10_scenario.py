
NAME = "Scale Obs 10"
DESCRIPTION = "Scalability Test with observation upscaling for WI 2020"

AGENTS = ['A', 'B', 'C', 'D']

AUTHORITIES = {}

OBSERVATIONS = [{'observation_id': 0, 'before': [], 'sender': 'A', 'receiver': 'B', 'author': 'A', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}, {'observation_id': 1, 'before': [0], 'sender': 'C', 'receiver': 'B', 'author': 'C', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}, {'observation_id': 2, 'before': [1], 'sender': 'A', 'receiver': 'B', 'author': 'A', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}, {'observation_id': 3, 'before': [2], 'sender': 'C', 'receiver': 'B', 'author': 'C', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}, {'observation_id': 4, 'before': [3], 'sender': 'A', 'receiver': 'B', 'author': 'A', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}, {'observation_id': 5, 'before': [4], 'sender': 'C', 'receiver': 'B', 'author': 'C', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}, {'observation_id': 6, 'before': [5], 'sender': 'A', 'receiver': 'B', 'author': 'A', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}, {'observation_id': 7, 'before': [6], 'sender': 'C', 'receiver': 'B', 'author': 'C', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}, {'observation_id': 8, 'before': [7], 'sender': 'A', 'receiver': 'B', 'author': 'A', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}, {'observation_id': 9, 'before': [8], 'sender': 'C', 'receiver': 'B', 'author': 'C', 'topic': 'Web Engineering', 'message': 'Redecentralization of the Web'}]

HISTORY = {'A': {'B': 1.0, 'C': 1.0, 'D': 1.0}, 'B': {'A': 0, 'C': 0, 'D': 1.0}, 'C': {'A': 1.0, 'B': 1.0, 'D': 1.0}, 'D': {'A': 1.0, 'B': 1.0, 'C': 1.0}}

TOPICS = {}

TRUST_THRESHOLDS = {'cooperation': 0.5, 'forgivability': -0.5}

WEIGHTS = {'direct experience': 1.0, 'recommendation': 1.0, 'popularity': 1.0, 'age': 1.0, 'agreement': 1.0, 'authority': 1.0, 'provenance': 1.0, 'recency': 1.0, 'related resource': 1.0, 'specificity': 1.0, 'topic': 1.0}

METRICS_PER_AGENT = {'A': ['direct experience', 'popularity', 'recommendation'], 'B': ['direct experience', 'popularity', 'recommendation'], 'C': ['direct experience', 'popularity', 'recommendation'], 'D': ['direct experience', 'popularity', 'recommendation']}
