import pathlib
import textwrap

import google.generativeai as genai

import PIL.Image
import time
import os

import random
import numpy as np
def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    # torch.manual_seed(seed)
    # torch.cuda.manual_seed(seed)
    # torch.backends.cudnn.deterministic = True
    # env.seed(seed)
seed_everything(1)

def random_generate_questions():
    if os.path.isdir("questions-hole-pos-50"):
        print("Questions are already generated")
        return
    os.makedirs("questions-hole-pos-50", exist_ok=False)
    os.makedirs("answers-hole-pos-50", exist_ok=False)
    for level in range(3,9):
        os.makedirs("questions-hole-pos-50/level%d"%(level))
        os.makedirs("answers-hole-pos-50/level%d"%(level))
        for question_id in range(100):
            # random ask a grid
            row_num = random.sample(range(level), 1)[0]
            col_num = random.sample(range(level), 1)[0]
            # find the GT
            with open("utils/maps-50-text/level%d/%d.txt"%(level, question_id), "r") as f:
                contents = f.read()
                rows = contents.split('\n')
                grid_content = rows[row_num][col_num]
            if grid_content == "H":
                answer = "Y"
            else:
                answer = "N"
            # write question and answer
            question = "Is there a hole in row %d, column %d?"%(row_num+1, col_num+1)
            with open("questions-hole-pos-50/level%d/%d.txt"%(level, question_id), "w") as f:
                f.write(question)
            with open("answers-hole-pos-50/level%d/%d.txt"%(level, question_id), "w") as f:
                f.write(answer)



levels = [3,4,5,6,7,8]
in_context_example_num = 0 # 0, 1, 2, 4, 8


GOOGLE_API_KEY='YOUR-API-KEY'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')
if in_context_example_num > 0:
    output_path = "output/output_img_%d/"%(in_context_example_num)
    input_backup_path = "input/input_backup_img_%d/"%(in_context_example_num)
else:
    output_path = "output/output_img/"
    input_backup_path = "input/input_backup_img/"

os.makedirs(output_path, exist_ok=True)
os.makedirs(input_backup_path, exist_ok=True)

EXAMPLE_DICT = {
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
}

# Prepare examples
for level in levels:
    for example_id in range(8):
        img_input = PIL.Image.open("example/level%d/img/%d.png"%(level, example_id))
        with open("example/level%d/question/%d.txt"%(level, example_id), "r") as f:
            question_input = f.read()
        with open("example/level%d/answer/%d.txt"%(level, example_id), "r") as f:
            answer_input = f.read()
        this_example = (img_input, question_input, answer_input)
        EXAMPLE_DICT[level].append(this_example)

# import ipdb; ipdb.set_trace()
for level in levels:
    os.makedirs(output_path + "level%d"%(level), exist_ok=True)
    os.makedirs(input_backup_path + "level%d"%(level), exist_ok=True)
    start_idx = 0
    end_idx = 100
    runned_term = 0
    map_path = "maps/level%d/img/"%(level)
    while True:
        try:
            curr_id = start_idx + runned_term
            if curr_id >= end_idx:
                break
            img_input = PIL.Image.open(map_path + "%d.png"%(curr_id))
            prompt_input_1 = '''
In this task, you will analyze a maze to determine if there is a hole in a specific position.
The following figure illustrates the appearances of the player, holes, lands, and the goal within the maze. You will need to focus on the appearance of the hole.
'''
            prompt_input_2 = '''
Here is an example to illustrate how to analyze and answer the question:
'''
            prompt_input_3 = '''
Example question: Is there a hole in row 3, column 3?

In this example:
- We check the position in row 3, column 3.
- According to the image, it is a land square. It does not contain a hole.
- Therefore, you will output "<Output> No".

Your output should be: "<Output> No" or "<Output> Yes", depending on whether there is a hole at the specified position.
'''
            question_examples = []
            answer_examples = []
            image_examples = []
            if in_context_example_num > 0:
                example_indices = random.sample(range(8), in_context_example_num)
                for example_index in example_indices:
                    this_example = EXAMPLE_DICT[level][example_index]
                    image_examples.append(this_example[0])
                    question_examples.append(this_example[1] + "\n")
                    answer_examples.append(this_example[2] + "\n\n")
            prompt_input_4 = "\n\nNow you will analyze the following maze and answer the question: "
            with open("maps/level%d/question/%d.txt"%(level, curr_id), "r") as f:
                prompt_input_5 = f.read()
            prompt_img_1 = PIL.Image.open('prompt-visual-images/system-figure-1.png')
            prompt_img_2 = PIL.Image.open('prompt-visual-images/system-figure-2.png')
            model_input_seq = [prompt_input_1, prompt_img_1, prompt_input_2, prompt_img_2, prompt_input_3]
            if in_context_example_num > 0:
                assert len(question_examples) == len(image_examples)
                assert len(question_examples) == in_context_example_num
                model_input_seq.append("## Example:\n")
                for example_index in range(in_context_example_num):
                    model_input_seq.append(image_examples[example_index])
                    model_input_seq.append(question_examples[example_index])
                    model_input_seq.append(answer_examples[example_index])
            model_input_seq += [prompt_input_4, img_input, prompt_input_5]

            response = model.generate_content(model_input_seq)
            with open(input_backup_path + "level%d/%d.txt"%(level, curr_id), "w") as f:
                contents = ""
                for input_prompt_index in range(len(model_input_seq)):
                    if type(model_input_seq[input_prompt_index]) == type("string"):
                        contents += model_input_seq[input_prompt_index]
                f.write(contents)
            with open(output_path + "level%d/%d.txt"%(level, curr_id), "w") as f:
                f.write(response.text)
            # import ipdb; ipdb.set_trace()
            # pass
            time.sleep(2)
            runned_term += 1
        except:
            time.sleep(2)
            pass



