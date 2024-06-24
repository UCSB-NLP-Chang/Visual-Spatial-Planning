# read a map, receive a solution, determine if the solution reaches the goal

import gym
from gym.envs.toy_text.frozen_lake import generate_random_map
import random
import os
import numpy as np
# from PIL import Image

count = 0
full_correct = 0
part_correct = 0
invalid = 0

level = 8

check_map_dir = "../../maps/level%d_text/"%(level)
check_answer_dir = "output/output_img/"

def find_symbol(map, symbol):
    # return a list indicating the coordinates of the symbol
    # e.g., [1, 2] = (row1, col2), all 0-index
    results = []
    for i in range(len(map)):
        for j in range(len(map)):
            if map[i][j] == symbol:
                results.append([i, j])
    return results



# import ipdb; ipdb.set_trace()

for test_id in range(100):
    # print(test_id)
    # map
    with open(check_map_dir + '%d.txt'%(test_id), 'r') as f:
        contents = f.read()
        rows = contents.split('\n')

    # answer
    player_pos = find_symbol(rows, 'S')[0]
    goal_pos = find_symbol(rows, 'G')[0]
    answer_set = set()
    if player_pos[0] > goal_pos[0]:
        answer_set.add('Below')
    elif player_pos[0] < goal_pos[0]:
        answer_set.add('Above')
    if player_pos[1] > goal_pos[1]:
        answer_set.add('Right')
    elif player_pos[1] < goal_pos[1]:
        answer_set.add('Left')
    count += len(answer_set)


    try:
        # action
        with open(check_answer_dir + 'level%d/%d.txt'%(level, test_id), 'r') as f:
            contents = f.read()
            answer_index = contents.find('<Output> ')
            if answer_index == -1:
                answer_index = contents.find('<Output>\n')
            # if answer_index == -1:
            #     answer_index = contents.find('<Ouput> ')
            # if answer_index == -1:
            #     answer_index = contents.find('<Ouput>\n')
            # if answer_index == -1:
            #     answer_index = contents.find('## Output ')
            # if answer_index == -1:
            #     answer_index = contents.find('## Output\n')
            if answer_index == -1:
                assert 0
            answer = contents[answer_index+9:]
            answer = answer.split(',')
            for answer_index in range(len(answer)):
                answer[answer_index] = answer[answer_index].replace('"', '')
                answer[answer_index] = answer[answer_index].replace("'", '')
                answer[answer_index] = answer[answer_index].replace("\n", '')
                answer[answer_index] = answer[answer_index].replace(".", '')
                answer[answer_index] = answer[answer_index].replace("*", '')
                answer[answer_index] = answer[answer_index].lstrip()
                answer[answer_index] = answer[answer_index].rstrip()

        # temp = env.render()
        # import ipdb; ipdb.set_trace()


        # import ipdb; ipdb.set_trace()
        ALL_CORR = True
        for answer_char in answer_set:
            if answer_char in answer:
                part_correct += 1
            else:
                ALL_CORR = False
                # print(test_id)
        if ALL_CORR:
            full_correct += 1
    except:
        # If not
        # count += 1
        invalid += 1
        print(test_id)
        # import ipdb; ipdb.set_trace()
        pass

print("Total tested: %d"%(count))
print("Part correct: %d"%(part_correct))
print("Each correct rate: %f"%(part_correct / count))
print("Full correct: %d"%(full_correct))
print("Invalid: %d"%(invalid))
