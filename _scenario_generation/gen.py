import getopt
import sys
from models.scenario_ct_random import Scenario


def main(argv):
    observations = 0
    agents = 0
    outfile = ''
    try:
        opts, _ = getopt.getopt(
            argv, "hm:a:o:", ["messages=", "agents=", "ofile"])
    except getopt.GetoptError:
        print('gen.py -m <number of messages> -a <number of agents> -o <output file>')
        sys.exit(2)
    if len(opts) == 0:
        print('gen.py -m <number of messages> -a <number of agents> -o <output file>')
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print('gen.py -m <number of messages> -a <number of agents> -o <output file>')
            sys.exit()
        elif opt in ('-m', '--messages'):
            observations = int(arg)
        elif opt in ('-a', '--agents'):
            agents = int(arg)
        elif opt in ('-o', '--ofile'):
            outfile = arg
    scenario = Scenario(observations, agents, outfile)
    scenario.generate_and_write_to_file()


if __name__ == "__main__":
    main(sys.argv[1:])
