import base64
import os
from mistralai import Mistral

import PIL.Image
import time
import os

import random
import numpy as np
def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
seed_everything(1)

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

# Retrieve the API key from environment variables
# api_key = "YOUR_API_KEY"

# Specify model
model = "pixtral-12b-2409"

# Initialize the Mistral client
client = Mistral(api_key=api_key)

levels = [1]
in_context_example_num = 0 # 0, 1, 2, 4, 8

if in_context_example_num > 0:
    assert 0
else:
    output_path = "your_output_path/"
    input_backup_path = "input-mistral/input_backup_img/"

os.makedirs(output_path, exist_ok=True)
os.makedirs(input_backup_path, exist_ok=True)
test_map_map = {0: 1, 1: 4, 2: 5, 3: 6, 4: 9}
import ipdb; ipdb.set_trace()
for level in levels:
    os.makedirs(output_path + "level%d"%(level), exist_ok=True)
    os.makedirs(input_backup_path + "level%d"%(level), exist_ok=True)
    start_idx = 0
    end_idx = 100
    runned_term = 0
    while True:
        try:
            curr_id = start_idx + runned_term
            if curr_id >= end_idx:
                break
            test_id = curr_id
            test_map_id = test_map_map[test_id // 20]
            test_map_subid = test_id % 20
            test_image = "../maps/level%d/test%d-%d.png"%(level, test_map_id, test_map_subid)
            example_image = "../prompt-visual-images/example.png"
            prompt_1 = '''As a professional pathfinder, your task is to analyze a map and find a route from the starting location to the goal. Since coding is not within your skill set, your approach relies on logical reasoning of the map.

## Game Setup
- The game presents a fully observable map.
- The starting location is marked with blue "S", and the goal is marked with red "G".
- Your goal is to find a path from the starting location to the goal.

## Moving Rules
- The action plan involves moves in four directions: 'W' (West), 'E' (east), 'N' (north), or 'S' (south).
- Each move is along with distances. Distances are measured by how many crossroads passed.
We provide an example to further illustrate the rules.
'''
            prompt_2 = '''In this provided example:
- You are now at the southwest of the goal.
- If you move north by 1 crossroad, you will be at the west of the goal.
- If you move east by 4 crossroads, you will be at the goal.
- IMPORTANT: Please ignore the name of the street and avenue. The numbers in the name cannot be used to compute how many crossroads need to be passed.

## Procedure and Output
Now you will solve the given maze. To solve it, please first analyze the relative spatial relation between the starting point and the goal (for example, southwest). Then, output a path using the format <Direction>: <Number of crossroads passed>. 
For example:
<Output>
1. North: 1
2. East: 4
means move north by 1 crossroad, and move east by 4 crossroads.
<Output>
1. South: 1
means move south by 1 crossroad.
Do not output any extra content after the above aggregated output.

Please output path for the following map:
'''
            prompt_examples = []
            image_examples = []
            test_image = encode_image(test_image)
            example_image = encode_image(example_image)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_1
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{example_image}"
                        },
                        {
                            "type": "text",
                            "text": prompt_2
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{test_image}"
                        },
                    ]
                }
            ]
            # import ipdb; ipdb.set_trace()
            chat_response = client.chat.complete(
                model=model,
                messages=messages,
                max_tokens=1000
            )
            time.sleep(3)
            # import ipdb; ipdb.set_trace()
            print(chat_response.choices[0].message.content)
            with open(output_path + "level%d/%d.txt"%(level, curr_id), "w") as f:
                f.write(chat_response.choices[0].message.content)
            time.sleep(2)
            runned_term += 1
        except:
            print("error")
            time.sleep(2)
            pass
        # except:
        #     import ipdb; ipdb.set_trace()
        #     pass







