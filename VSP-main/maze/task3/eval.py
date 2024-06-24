# read a map, receive a solution, determine if the solution reaches the goal

import gym
from gym.envs.toy_text.frozen_lake import generate_random_map
import random
import os
import numpy as np
# from PIL import Image



levels = [3,4,5,6,7,8]
# import ipdb; ipdb.set_trace()
for level in levels:
# level = 3
    count = 0
    correct = 0
    invalid = 0

    gt_answer_dir = "../maps/level%d/answer/"%(level)
    check_answer_dir = "output/output_img/level%d/"%(level)

    for test_id in range(100):
        try:
            # parse answer from the output
            output_path = check_answer_dir + "%d.txt"%(test_id)
            with open(output_path, "r") as f:
                contents = f.read()
                # answer_index = contents.find("<Output>")
                # answer = contents[answer_index+len("<Output>"):]
                # if answer_index == -1:
                answer_index = contents.find("<Answer>")
                answer = contents[answer_index+len("<Answer>"):]
                if answer_index == -1:
                    answer_index = contents.find("**Answer")
                    answer = contents[answer_index+len("**Answer"):]
                if answer_index == -1:
                    answer_index = contents.find("Answer")
                    answer = contents[answer_index+len("Answer"):]
                answer = answer.replace('"', '')
                answer = answer.replace('*', '')
                answer = answer.replace(':', '')
                answer = answer.replace("'", '')
                answer = answer.replace("\n", '')
                answer = answer.replace(".", '')
                answer = answer.replace("(", '')
                answer = answer.replace(")", '')
                answer = answer.replace("<", '')
                answer = answer.replace(">", '')
                answer = answer.replace("`", '')
                answer = answer.lstrip()
                answer = answer.rstrip()
                # import ipdb; ipdb.set_trace()
                assert answer in ['A', 'B', 'C', 'D']
                    # pass
                # else:
                #     assert 
                #     if 'A' in answer and 'B' not in answer and 'C' not in answer and 'D' not in answer:
                #         answer = 'A'
                #     elif 'B' in answer and 'C' not in answer and 'D' not in answer:
                #         answer = 'B'
                #     elif 'C' in answer and 'D' not in answer:
                #         answer = 'C'
                #     elif 'D' in answer:
                #         answer = 'D'
            # parse GT from recorded file
            gt_path = gt_answer_dir + "%d.txt"%(test_id)
            with open(gt_path, "r") as f:
                contents = f.read()
                rows = contents.split('\n')
                assert len(rows) == 5
                gt = int(rows[-1])
                key_dict = {0: 'A', 1: 'B', 2: 'C', 3:'D'}
                gt = key_dict[gt]
            if answer == gt:
                correct += 1
            # else:
            #     print(answer, test_id)
            count += 1
        except:
            # print(test_id)
            # import ipdb; ipdb.set_trace()
            invalid += 1
            count += 1
            pass
    print("------Level %d-------"%(level))
    print("Total tested: %d"%(count))
    print("Total correct: %d"%(correct))
    print("Total invalid: %d"%(invalid))
