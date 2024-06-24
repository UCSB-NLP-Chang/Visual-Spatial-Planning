import csv
import os

count_corr = [0,0,0,0,0]
invalid = [0,0,0,0,0]

for level in [1,3,5,7,9]:
    for test_id in range(100):
        with open("../maps/level_step%d/answer/%d.txt"%(level, test_id), "r") as f:
            gt_records = f.read()
        try:
            with open("output/output_img/level%d/%d.txt"%(level, test_id), "r") as f:
                # import ipdb; ipdb.set_trace()
                answer = f.read()
                plan_answer_index = answer.find("<Output>")
                if plan_answer_index != -1:
                    answer = answer[plan_answer_index+len("<Output>"):plan_answer_index+len("<Output>")+10]
                else:
                    plan_answer_index = answer.find("**Output**")
                    if plan_answer_index != -1:
                        answer = answer[plan_answer_index+len("**Output**"):plan_answer_index+len("**Output**")+10]
                    else:
                        plan_answer_index = answer.find("Output")
                        answer = answer[plan_answer_index+len("Output"):plan_answer_index+len("Output")+10]
                        if plan_answer_index == -1:
                            invalid[level//2] += 1
                
                # import ipdb; ipdb.set_trace()
                answer = answer.replace('"', '')
                answer = answer.replace("'", '')
                answer = answer.replace("\n", '')
                answer = answer.replace(".", '')
                answer = answer.replace(":", '')
                answer = answer.replace("-", '')
                answer = answer.replace("*", '')
                answer = answer.lstrip()
                answer = answer.rstrip()
                answer = answer.lower()
                # if test_id == 99:
                #     import ipdb; ipdb.set_trace()
                if "yes" in answer.lower() and "no" not in answer.lower() and gt_records == "Y":
                    count_corr[level//2] += 1
                    # print(test_id)
                elif "no" in answer.lower() and "yes" not in answer.lower() and gt_records == "N":
                    count_corr[level//2] += 1
                    # print(test_id)
                else:
                    print(answer, test_id)
                # else:
                #     print(answer, test_id)
        except:
            invalid[level//2] += 1
print(count_corr)
print(invalid)
# import ipdb; ipdb.set_trace()
# pass
