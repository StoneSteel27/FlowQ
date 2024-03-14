import argparse
import uuid
from .FlowQluster import FlowQluster

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="python -m FlowQ.cluster"
                                     ,description='Initialize FlowQ cluster')
    parser.add_argument('-c', '--channel',required=True,type=str,help='Communication Channel Name')
    args = parser.parse_args()
    flow = FlowQluster(args.channel)
    bot_name = str(uuid.uuid4())[:4]
    flow.connect(bot_name)
    flow.initialize_cluster()
