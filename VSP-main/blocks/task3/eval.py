import csv
import os

def clear_answer(plan):
    plan = plan.replace('"', '')
    plan = plan.replace("'", '')
    plan = plan.replace("\n", '')
    plan = plan.replace(".", '')
    plan = plan.replace("*", '')
    plan = plan.lstrip()
    plan = plan.rstrip()
    return plan

answer_dict = {0: "A", 1: 'B', 2: 'C', 3: 'D'}

# import ipdb; ipdb.set_trace()
count_corr = [0,0,0]
invalid = [0,0,0]
for level in [3,4,5]:
    with open("../level%d/annotation.txt"%(level), "r") as f:
        gt_records = f.read().split('\n')[:-1]
    for test_id in range(100):
        try:
            curr_record = gt_records[test_id]
            with open("output/output_img/level%d/%d.txt"%(level, test_id), "r") as f: # img5, text4
                answer = f.read()
                answer_index = answer.find("<Output>")
                if answer_index == -1:
                    answer_index = answer.find("Output")
                    answer = answer[(answer_index + len("Output")):]
                else:
                    answer = answer[(answer_index + len("<Output>")):]
                answer_possible_end_index = answer.find('\n')
                if answer_possible_end_index != -1:
                    answer = answer[:answer_possible_end_index]
                answer = clear_answer(answer)
                # import ipdb; ipdb.set_trace()
            if answer_dict[int(curr_record)] == answer.upper():
                count_corr[level-3] += 1
            else:
                print(answer, test_id)
                pass
        except:
            invalid[level-3] += 1
            # print(test_id)
print(count_corr)
print(invalid)
print("")