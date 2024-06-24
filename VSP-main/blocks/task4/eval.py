import csv
import os

count_corr = [0,0,0,0]
invalid = [0,0,0,0]

for level in [1,3,5,7]:
    with open("../level%d/annotation.txt"%(level), "r") as f:
        gt_records = f.read().split('\n')[:-1]
    for test_id in range(100):
        try:
            with open("output/output_img/level%d/%d.txt"%(level, test_id), "r") as f:
                answer = f.read()
                plan_answer_index = answer.find("<Output>")
                answer = answer[plan_answer_index+len("<Output>"):]
                answer = answer.replace('"', '')
                answer = answer.replace("'", '')
                answer = answer.replace("\n", '')
                answer = answer.replace(".", '')
                answer = answer.lstrip()
                answer = answer.rstrip()
                answer = answer.lower()
                if answer == 'yes' and str(test_id) in gt_records:
                    count_corr[level//2] += 1
                    # print(test_id)
                elif answer == 'no' and str(test_id) not in gt_records:
                    count_corr[level//2] += 1
                    # print(test_id)
                # else:
                #     print(answer, test_id)
        except:
            invalid[level//2] += 1
print(count_corr)
print(invalid)
# import ipdb; ipdb.set_trace()
# pass
