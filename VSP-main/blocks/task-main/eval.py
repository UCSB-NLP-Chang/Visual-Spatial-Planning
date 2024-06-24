# input: actions, begin state, end state
# output: judge whether reach the end state

import csv
import os
import copy

def move(input_s, action):
    # one action consequence
    elems = action[len("move("):-1].split(',')
    action_from = elems[0][0]
    action_to = elems[1]
    action_from = action_from.lstrip()
    action_from = action_from.rstrip()
    action_to = action_to.lstrip()
    action_to = action_to.rstrip()
    if action_to != "table":
        action_to = action_to[0]
    # if no stack having "action_from" at top -> invalid move. Else, remove the stack "action_from"
    FOUND_FROM_BLOCK = False
    for stack_id, each_stack in enumerate(input_s):
        if len(each_stack) == 0:
            continue
        if each_stack[-1] == action_from.upper():
            FOUND_FROM_BLOCK = True
            break
    if not FOUND_FROM_BLOCK:
        return False
    input_s[stack_id] = input_s[stack_id][:-1]
    # if no stack having "action_to" at top and the "action_to" is "table" -> invalid move
    FOUND_TO_BLOCK = False
    if action_to == "table":
        FOUND_TO_BLOCK = True
    for stack_id, each_stack in enumerate(input_s):
        if len(each_stack) != 0 and each_stack[-1] == action_to.upper():
            FOUND_TO_BLOCK = True
            to_stack_id = stack_id
            break
    if not FOUND_TO_BLOCK:
        return False
    # actual move
    if action_to == "table":
        for stack_id, each_stack in enumerate(input_s):
            if len(each_stack) == 0:
                each_stack.append(action_from.upper())
                break
    else:
        input_s[to_stack_id].append(action_from.upper())
    return input_s


def equivalence(stacks_1, stacks_2):
    # determine if two stacks are equivalent.
    stack2_ids = []
    for each_stack_1 in stacks_1:
        if len(each_stack_1) == 0:
            continue
        FOUND_CURR_STACK = False
        curr_checking_block = each_stack_1[-1]
        for stack2_id, each_stack_2 in enumerate(stacks_2):
            if len(each_stack_2) == 0:
                continue
            if each_stack_2[-1] != curr_checking_block:
                continue
            while True:
                if len(each_stack_1) == 0  or len(each_stack_2) == 0 or each_stack_1[:-1] != each_stack_2[:-1]:
                    break
                each_stack_1 = each_stack_1[:-1]
                each_stack_2 = each_stack_2[:-1]
                if len(each_stack_1) == len(each_stack_2) and len(each_stack_1) == 0:
                    FOUND_CURR_STACK = True
                    stack2_ids.append(stack2_id)
                    break
        if not FOUND_CURR_STACK:
            return False
    for stack2_id, each_stack_2 in enumerate(stacks_2):
        if stack2_id not in stack2_ids and len(each_stack_2) != 0:
            return False
    return True


def eval(input_s, output_s, actions):
    # read input_s+output_s, convert it into a bunch of stacks
    # input_s example G00000-R00000-P00000-YB0000-000000-000000-000000
    stacks = []
    target_stacks = []
    input_stack = input_s.split("-")
    target_stack = output_s.split('-')
    for each_stack in input_stack:
        curr_stack = []
        for each_block in each_stack:
            if each_block != "0":
                curr_stack.append(each_block)
        stacks.append(curr_stack)
    for each_stack in target_stack:
        curr_stack = []
        for each_block in each_stack:
            if each_block != "0":
                curr_stack.append(each_block)
        target_stacks.append(curr_stack)
    # assert len(stacks) == 7
    # determine if the action can bring stacks to target_stacks
    # action example ['move(y,table,0)', 'move(g,table,1)', 'move(o,g,2)']
    # actions = actions.split(' ')
    # import ipdb; ipdb.set_trace()
    for each_action in actions:
        if each_action == "":
            continue
        new_stacks = move(copy.deepcopy(stacks), each_action)
        if not new_stacks: # invalid move
            pass
        else:
            stacks = new_stacks
    return equivalence(stacks, target_stacks)


# small test
import ipdb; ipdb.set_trace()
count_corr = [0,0,0,0]
invalid = [0,0,0,0]
for level in [1,3,5,7]:
    with open("../level%d/info.txt"%(level), "r") as f:
        gt_records = f.read().split('\n')[:-1]
    for test_id in range(100):
        try:
            curr_record = gt_records[test_id].split('\t')
            input_state = curr_record[0]
            output_state = curr_record[2]
            with open("output-old/output_img/level%d/%d.txt"%(level, test_id), "r") as f:
                answer = f.read()
                plan_answer_index = answer.find("<Output>")
                plans = answer[plan_answer_index+len("<Output>\n"):]
                # plan_answer_index = answer.find("* Plan")
                # plans = answer[plan_answer_index+len("* Plan\n"):]
                plans = plans.split('\n')
                for plan_id, plan in enumerate(plans):
                    plan = plan[2:]
                    plan = plan.replace('"', '')
                    plan = plan.replace("'", '')
                    plan = plan.replace("\n", '')
                    plan = plan.replace(".", '')
                    plan = plan.lstrip()
                    plan = plan.rstrip()
                    if plan[:4] != "move":
                        plans[plan_id] = ''
                    else:
                        plans[plan_id] = plan

                # print(plans)
                result = eval(input_state, output_state, plans)
                if result:
                    count_corr[level//2] += 1
                    # print(test_id)
        except:
            invalid[level//2] += 1
            # import ipdb; ipdb.set_trace()
            # print(plans, test_id)
print(count_corr)
print(invalid)
# import ipdb; ipdb.set_trace()
# pass

print("")
