# read a map, receive a solution, determine if the solution reaches the goal

import gym
from gym.envs.toy_text.frozen_lake import generate_random_map
import random
import os
import numpy as np
# from PIL import Image

levels = [3,4,5,6,7,8]
for level in levels:
    count = 0
    correct = 0
    invalid = 0

    yes_c = 0
    yes_w = 0

    gt_answer_dir = "maps/level%d/answer/"%(level)
    check_answer_dir = "output/output_pure_text/level%d/"%(level)

    # import ipdb; ipdb.set_trace()
    for test_id in range(100):
        try:
            # parse answer from the output
            output_path = check_answer_dir + "%d.txt"%(test_id)
            with open(output_path, "r") as f:
                contents = f.read()
                answer_index = contents.find("<Output>")
                answer = contents[answer_index+len("<Output>"):]
                # if answer_index == -1:
                # answer_index = contents.find("Answer:")
                # answer = contents[answer_index+len("Answer:"):]
                answer = answer.replace('"', '')
                answer = answer.replace("'", '')
                answer = answer.replace("\n", '')
                answer = answer.replace(".", '')
                answer = answer.replace("(", '')
                answer = answer.replace(")", '')
                answer = answer.lstrip()
                answer = answer.rstrip()
                answer = answer.lower()
                # import ipdb; ipdb.set_trace()
                assert answer in ['yes', 'no']
            # import ipdb; ipdb.set_trace()
            # parse GT from recorded file
            gt_path = gt_answer_dir + "%d.txt"%(test_id)
            with open(gt_path, "r") as f:
                gt = f.read()
                key_dict = {'Y': 'yes', 'N': 'no'}
                gt = key_dict[gt]
            if answer == gt:
                correct += 1
                if answer == 'yes':
                    yes_c += 1
            else:
                if answer == 'yes':
                    yes_w += 1
            count += 1
            # print(answer)
        except:
            # import ipdb; ipdb.set_trace()
            invalid += 1
            count += 1
            pass

    # print(yes_c)
    # print(yes_w)
    print("=====Curr Level: %d======"%(level))
    print("Total tested: %d"%(count))
    print("Total correct: %d"%(correct))
    print("Total invalid: %d"%(invalid))
