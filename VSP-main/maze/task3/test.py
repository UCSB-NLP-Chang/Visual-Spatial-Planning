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

loop_time = 0

EXAMPLE_DICT = {
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: []
}

# Prepare examples
for level in levels:
    for example_id in range(8):
        example_path = "example/level%d/img/"%(level)
        img_input = PIL.Image.open(example_path + "%d.png"%(example_id))
        with open("example/level%d/question/%d.txt"%(level, example_id), "r") as f:
            example_candidates = f.read()
        with open("example/level%d/analysis/%d.txt"%(level, example_id), "r") as f:
            text_input = f.read()
        this_example = (img_input, example_candidates, text_input)
        EXAMPLE_DICT[level].append(this_example)

import ipdb; ipdb.set_trace()
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
In this task, you will analyze a maze presented in an image. Later, you will be presented with four choices, each offering a textual representation of a candidate maze. You will need to choose the representation that exactly reflects the contents of the given image.
The following figure illustrates the appearances of the player, holes, lands, and the goal within the maze in the image.
'''
            prompt_input_2 = '''
This is how the player, the holes (non-safe grid), the lands (safe grids), and the goals look like in a map:
- The player is represented as "@"
- The hole is represented as "#"
- The safe grid is represented as "_"
- The goal is represented as "*"
- If the player is at the goal (at this case the game is solved), that grid is represented as "%"

We provide an example to illustrate how to interpret the input, candidates, and answer the question. Here is the image input:
'''
            prompt_input_3 = '''
Here are the textual candidates:

(A)
| | Col 1 | Col 2 | Col 3 |
| Row 1 | # | _ | _ |
| Row 2 | # | @ | # |
| Row 3 | _ | * | _ |

(B)
| | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 |
| Row 1 | _ | _ | _ | _ | _ |
| Row 2 | _ | # | _ | _ | _ |
| Row 3 | _ | # | * | _ | # |
| Row 4 | _ | @ | _ | _ | _ |
| Row 5 | _ | _ | _ | # | _ |

(C)
| | Col 1 | Col 2 | Col 3 | Col 4 |
| Row 1 | @ | # | _ | _ |
| Row 2 | _ | _ | _ | _ |
| Row 3 | _ | _ | _ | _ |
| Row 4 | # | _ | _ | * |

(D)
| | Col 1 | Col 2 | Col 3 | Col 4 |
| Row 1 | _ | _ | _ | _ |
| Row 2 | * | _ | _ | _ |
| Row 3 | @ | _ | # | _ |
| Row 4 | _ | _ | _ | # |

Here is an example of how to analyze and answer the question:
- First, we focus on the difference of the maze shape betweeen the candidates and the input image.
- We begin by examining the input image. It is a 4-by-4 maze. We then review the candidates. Candidate A is a 3-by-3 maze. Therefore, it is not the correct answer. Similarly, Candidate B is a 5-by-5 maze, which also cannot be correct. Both Candidate C and Candidate D are 4-by-4 mazes. Now we only need to choose from them.
- For the remaining candidates, we compare the positions of the players, goals, and the holes in the maze.
- We first check the input image. What is the position of the player in the image? The player is in row 1, column 1. We then check the remaining candidates. For Candidate C, the textual representation indicates the player is also at row 1, column 1, matching the input image. For Candidate D, the player is located at row 3, column 1. Hence, Candidate D is not the correct answer.
- We double check the remaining Candidate C, and it correctly shows the position of the player, holes, and the goal. It is therefore the correct answer.
<Answer> C

Your output should consist of two parts:
1. First, analysis the input image and candidates similar to the reasoning process above.
2. Following the reasoning process, output answer as "<Answer> <Choice>", where "<Choice>" is one of {A,B,C,D}.
Important: Note that there will be only one correct answer. If you find no answer or multiple answers, you must go back and recheck your reasoning process. You are not allowed to provide 0 or more than 1 answer.
'''
            candidate_examples = []
            prompt_examples = []
            image_examples = []
            if in_context_example_num > 0:
                prompt_examples.append("## Example:\n")
                example_indices = random.sample(range(8), in_context_example_num)
                for example_index in example_indices:
                    this_example = EXAMPLE_DICT[level][example_index]
                    image_examples.append(this_example[0])
                    candidate_examples.append(this_example[1])
                    prompt_examples.append(this_example[2] + "\n")
            prompt_input_4 = "\nNow answer the question below. Here is the image input:"
            prompt_input_5 = "\nHere are the textual candidates:"
            prompt_img_1 = PIL.Image.open('prompt-visual-images/system-figure-1.png')
            prompt_img_2 = PIL.Image.open('prompt-visual-images/system-figure-2.png')
            model_input_seq = [prompt_input_1, prompt_img_1, prompt_input_2, prompt_img_2, prompt_input_3]
            if in_context_example_num > 0:
                assert len(prompt_examples) == len(image_examples) + 1
                assert len(prompt_examples) == in_context_example_num + 1
                model_input_seq.append(prompt_examples[0])
                for example_index in range(in_context_example_num):
                    model_input_seq.append(image_examples[example_index])
                    model_input_seq.append(candidate_examples[example_index])
                    model_input_seq.append(prompt_examples[example_index+1])
            with open("maps/level%d/question/%d.txt"%(level, curr_id), 'r') as f:
                candidates_str = f.read()
            # candidates_str = ""
            # # build candidates strings
            # wrong_choices = []
            # wrong_sizes = [3,4,5,6,7,8]
            # wrong_sizes.remove(level)
            # picked_choice = random.sample(wrong_sizes,2)
            # # candidate with wrong size: 2
            # used_candidates = []
            # for select_level in picked_choice:
            #     select_map = random.sample(range(100), 1)[0]
            #     with open("../maps/level%d_table/%d.txt"%(select_level, select_map), "r") as f:
            #         select_content = f.read()
            #         wrong_choices.append(select_content)
            #         used_candidates.append("%d-%d"%(select_level, select_map))
            # # candidate with correct size: 1
            # select_map = random.sample([t for t in range(100) if t != curr_id], 1)[0]
            # with open("../maps/level%d_table/%d.txt"%(level, select_map), "r") as f:
            #     select_content = f.read()
            #     wrong_choices.append(select_content)
            #     used_candidates.append("%d-%d"%(level, select_map))
            # # correct candidate
            # with open("../maps/level%d_table/%d.txt"%(level, curr_id), "r") as f:
            #     correct_candidate = f.read()
            # # build candidate order
            # correct_candidate_id = random.sample(range(4), 1)[0]
            # correct_size_candidate_id = random.sample([x for x in range(4) if x != correct_candidate_id], 1)[0]
            # candidate_order_list = []
            # used_candidates_order_list = []
            # wrong_size_index = 0 # This is to go through two incorrect caniddates with incorrect size
            # for candidate_index in range(4):
            #     if candidate_index == correct_candidate_id:
            #         candidate_order_list.append(correct_candidate)
            #         used_candidates_order_list.append("%d-%d"%(level, curr_id))
            #     elif candidate_index == correct_size_candidate_id:
            #         candidate_order_list.append(wrong_choices[-1])
            #         used_candidates_order_list.append(used_candidates[-1])
            #     else:
            #         candidate_order_list.append(wrong_choices[wrong_size_index])
            #         used_candidates_order_list.append(used_candidates[wrong_size_index])
            #        wrong_size_index += 1
            ## save input maps, and correct answer
            # with open("answer-key-whole-map-9/level%d/%d.txt"%(level,curr_id), 'w') as f:
            #     solutions_txt = ""
            #     for each_used_candidate in used_candidates_order_list:
            #         solutions_txt += each_used_candidate
            #         solutions_txt += "\n"
            #     solutions_txt += "%s"%(correct_candidate_id)
            #     f.write(solutions_txt)
            ## build candidate string
            # candidates_str = "\n(A)\n" + candidate_order_list[0] + "\n(B)\n" + candidate_order_list[1] + "\n(C)\n" + candidate_order_list[2] + "\n(D)\n" + candidate_order_list[3]
            model_input_seq += [prompt_input_4, img_input, prompt_input_5, candidates_str]
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






# pass



# cookie_picture = [{
#     'mime_type': 'image/png',
#     'data': Path('cookie.png').read_bytes()
# }]
# prompt = "Do these look store-bought or homemade?"

# response = model.generate_content(
#     model="gemini-pro-vision",
#     content=[prompt, cookie_picture]
# )
# print(response.text)