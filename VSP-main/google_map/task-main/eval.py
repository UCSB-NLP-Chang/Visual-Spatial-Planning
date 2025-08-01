import pickle as pkl
import os

output_dir = "your_output_dir"

corr = 0
total = 0
test_map_map = {0: 1, 1: 4, 2: 5, 3: 6, 4: 9}
import ipdb; ipdb.set_trace()
for test_id in range(100):
    try:
        test_map_id = test_map_map[test_id // 20]
        test_map_subid = test_id % 20
        file_path = output_dir + "%d.txt"%(test_id)
        with open(file_path, "r") as f:
            contents = f.read()
            c_index = contents.find("Output")
            if c_index == -1:
                c_index = contents.find("Path")
            contents = contents[c_index+7:]
            contents = contents.replace('"', '')
            contents = contents.replace("'", '')
            contents = contents.replace(".", '')
            contents = contents.lstrip()
            contents = contents.rstrip()
            contents = contents.split('\n')
            north_south = 0
            east_west = 0
            for i in range(len(contents)):
                if "north" in contents[i].lower():
                    num = int(contents[i].lower().split("north:")[-1])
                    north_south += num
                if "south" in contents[i].lower():
                    num = int(contents[i].lower().split("south:")[-1])
                    north_south -= num
                if "east" in contents[i].lower():
                    num = int(contents[i].lower().split("east:")[-1])
                    east_west += num
                if "west" in (contents[i].lower()):
                    num = int(contents[i].lower().split("west:")[-1])
                    east_west -= num
        with open("maps/level1/answer-%d.pkl"%(test_map_id), "rb") as f:
            gt_answer = pkl.load(f)[test_map_subid]
            gt_north_south = gt_answer[0]
            gt_east_west = -gt_answer[1]

        if gt_north_south == north_south and gt_east_west == east_west:
            corr += 1
            total += 1
        else:
            total += 1
    except:
        total += 1
        print(test_id)

print(total)
print(corr)
