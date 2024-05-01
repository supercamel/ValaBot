import json
import random
# iterate the jsonl file one line at a time

start_text = "<｜fim▁begin｜>"
end_text = "<｜fim▁end｜>"
hole_text = "<｜fim▁hole｜>"
path = "vala_dataset.jsonl"
jsonl_file = open(path, "r")
deepseek_jsonl = open("deepseek.jsonl", "w")
arr = []
ooba_arr = []
for line in jsonl_file:
    # load the json object
    data = json.loads(line)
    instruction = data["instruction"]
    output = data["output"]

    if(output == "}"):
        continue
    if(len(output) < 10):
        continue
    if(len(instruction) < 20):
        continue

    # remove ```vala from the start of the instruction
    if(instruction.startswith("```vala")):
        instruction = instruction[7:]
    # remove ``` from the end of the instruction
    if(instruction.endswith("```")):
        instruction = instruction[:-3]

    # replace all instances of "<|fim_hole|>" with "<｜fim▁hole｜>"
    instruction = instruction.replace("<|fim_hole|>", hole_text)

    # if instruction contains multiple holes, skip it
    if(instruction.count(hole_text) != 1):
        continue
    
    # 50% chance to move a few characters from the start of the output to before the hole in the instruction
    if(random.random() < 0.5):
        start_of_output = output[:3]
        output = output[3:]

        # insert the start of the output before the hole in the instruction
        instruction = instruction.replace(hole_text, start_of_output + hole_text)

    # format the json object ｜
    formatted_json = start_text + instruction + end_text + output 
    if(len(formatted_json) > 2048):
        continue
    arr.append({
        "text": formatted_json
    })

    ooba_obj = {
        "instruction": instruction,
        "output": output
    }

    deepseek_jsonl.write(json.dumps(ooba_obj) + "\n")

# write the formatted json objects to a new json file
with open("vala_dataset.json", "w") as f:
    json.dump(arr, f)
    