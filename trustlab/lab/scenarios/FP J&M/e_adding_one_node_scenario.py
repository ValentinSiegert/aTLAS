#basic scenario with additional Node
NAME = "Adding new Agent"
DESCRIPTION = "This is a basic scenario with an added Agents."

AGENTS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

AUTHORITY = ['B', 'E']

OBSERVATIONS = ['A,B,a,k1,apple', 'B,C,g,k1,banana', 'C,D,e,k1,pineapple', 'D,E,g,k2,cauliflower', 'E,F,a,k1,apricot', 'F,G,b,k1,berrie', 'G,A,d,k1,artichoke', 'A,G,c,k1,cherries', 'B,F,g,k1,apple', 'C,E,e,k2,onion', 'D,C,f,k1,banana', 'E,B,a,k1,pineapple', 'F,C,b,k3,house', 'G,B,e,k2,cauliflower', 'A,F,b,k1,apricot', 'B,E,c,k2,artichoke', 'C,F,d,k3,brick', 'D,B,e,k1,pineapple', 'E,A,f,k3,house', 'F,B,g,k2,cauliflower', 'G,C,a,k1,apricot', 'A,E,b,k2,artichoke', 'B,D,c,k3,brick', 'C,B,d,k2,cauliflower', 'D,A,e,k1,cherries', 'E,C,f,k1,banana', 'F,A,g,k3,brick', 'G,D,a,k2,onion', 'A,C,g,k1,banana', 'B,G,f,k2,artichoke', 'C,G,e,k3,house', 'D,F,c,k2,cauliflower', 'E,G,d,k1,banana', 'F,D,a,k2,onion', 'G,E,b,k1,apricot', 'A,D,c,k1,banana', 'B,A,d,k3,brick', 'C,A,e,k3,house', 'D,G,f,k2,onion', 'E,D,g,k3,brick', 'F,E,a,k1,pineapple', 'G,F,b,k2,cauliflower', 'H,C,b,k1,cherries', 'H,E,a,k1,apricot', 'H,B,b,k1,banana', 'H,E,f,k2,onion', 'H,A,b,k1,cherries']

HISTORY = {'A': {'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}, 'B': {'A': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}, 'C': {'A': 0, 'B': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}, 'D': {'A': 0, 'B': 0, 'C': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}, 'E': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0, 'G': 0, 'H': 0}, 'F': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'G': 0, 'H': 0}, 'G': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'H': 0}, 'H': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0}}

INSTANT_FEEDBACK = {'k0': 0, 'k1': 0.6, 'k2': 0.3, 'k3': -0.7}


TRUST_THRESHOLDS = {'upper_limit': 0.75, 'lower_limit': -0.75}


WEIGHTS = {'direct experience': 1.2, 'recommendation': 1.2, 'popularity': 1.2, 'age': 1.2, 'agreement': 1.2, 'authority': 1.2, 'provenance': 1.2, 'recency': 1.2, 'related resource': 1.2, 'specificity': 1.2, 'topic': 1.2}

METRICS_PER_AGENT = {'A': ['age', 'agreement', 'authority', 'direct experience', 'popularity', 'provenance', 'recency', 'recommendation', 'related resource', 'specificity', 'topic'], 'B': ['age', 'agreement', 'authority', 'direct experience', 'popularity', 'provenance', 'recency', 'recommendation', 'related resource', 'specificity', 'topic'], 'C': ['age', 'agreement', 'authority', 'direct experience', 'popularity', 'provenance', 'recency', 'recommendation', 'related resource', 'specificity', 'topic'], 'D': ['age', 'agreement', 'authority', 'direct experience', 'popularity', 'provenance', 'recency', 'recommendation', 'related resource', 'specificity', 'topic'], 'E': ['age', 'agreement', 'authority', 'direct experience', 'popularity', 'provenance', 'recency', 'recommendation', 'related resource', 'specificity', 'topic'], 'F': ['age', 'agreement', 'authority', 'direct experience', 'popularity', 'provenance', 'recency', 'recommendation', 'related resource', 'specificity', 'topic'], 'G': ['age', 'agreement', 'authority', 'direct experience', 'popularity', 'provenance', 'recency', 'recommendation', 'related resource', 'specificity', 'topic'], 'H': ['age', 'agreement', 'authority', 'direct experience', 'popularity', 'provenance', 'recency', 'recommendation', 'related resource', 'specificity', 'topic']}


