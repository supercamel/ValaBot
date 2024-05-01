import os
import json
import re
import random
from common import tryMessages

def process_file(path):
    with open(path, "r") as f:
        vala_source = f.read()

    code_chunks = divide_code(vala_source)

    for chunk in code_chunks:    
        chunk_string = "\n".join(chunk)
        max_range = 3 if len(chunk_string) < 50 else 1
        
        for _ in range(max_range):
            response = "```vala\n" + chunk_string + "\n```"
            process_response_llm(response)

def divide_code(vala_source, max_chunk_size=40):
    n_lines = vala_source.count("\n")
    return [vala_source.splitlines()[i:i+max_chunk_size] for i in range(0, n_lines, max_chunk_size)]

def process_block_hole(segment):
    lines = segment.split("\n")
    n_lines = len(lines)
    if n_lines > 3:
        # Initialize a stack for bracket matching
        stack = []
        last_bracket_line = None
        last_bracket_pos = None
        end_bracket_line = None
        end_bracket_pos = None

        # Scan all lines for brackets and determine the block to replace
        for line_index, line in enumerate(lines):
            for char_index, char in enumerate(line):
                if char == '{':
                    stack.append((line_index, char_index))
                elif char == '}':
                    if stack:
                        start_line, start_pos = stack.pop()
                        last_bracket_line = start_line
                        last_bracket_pos = start_pos
                        end_bracket_line = line_index
                        end_bracket_pos = char_index

        if last_bracket_line is not None and end_bracket_line is not None:
            # Extract and replace the block
            block_lines = lines[last_bracket_line:end_bracket_line+1]
            block_lines[0] = block_lines[0][:last_bracket_pos+1]
            block_lines[-1] = block_lines[-1][end_bracket_pos:]
            lines[last_bracket_line:end_bracket_line+1] = block_lines

            segment_copy = "\n".join(lines)
            data = {
                "instruction": segment_copy,
                "output": segment_copy.strip()
            }

            print("Block hole")
            print(json.dumps(data, indent=2))

            return True
    return False


def process_response_rules_based(response):
    for segment in response.split("```vala"):
        segment = segment.strip().strip("```")
        n_lines = segment.count("\n")
        
        if n_lines < 2:
            continue

        for _ in range(3):
            lines = segment.split("\n")
            if(process_block_hole(segment)):
                break 

            # single line hole
            r = int(random.triangular(0, n_lines, n_lines // 2))
            
            start_line = next((i for i in range(r, n_lines) if is_valid_line(lines[i])), None)
            
            if start_line is None:
                continue
            
            hole = lines[start_line].lstrip()
            placeholder = hole[:len(hole) - len(hole.lstrip())] + "<|fim_hole|>"
            
            if not is_valid_hole(hole):
                continue
            
            if hole.startswith(("public", "private", "return", "if", "for", "while", "var", "int", "double")):
                keyword = re.search(r"\b(public|private|return|if|for|while|var|int|double)\b", hole).group(0)
                # remove the keyword from the hole
                hole = hole.replace(keyword, "").strip()
                # add the keyword to the placeholder
                placeholder = keyword + " " + placeholder
                
            elif "=" in hole:
                if random.random() < 0.5:
                    parts = hole.split("=")
                    if len(parts) > 1:  # Ensure there is something after the '='
                        placeholder = parts[0].strip() + " = " + placeholder  # Place the placeholder right after the '='
                        hole = parts[1].strip()  # Keep everything after the '=' as the new hole

            lines[start_line] = placeholder
            segment_copy = "\n".join(lines)

            data = {
                "instruction": segment_copy,
                "output": hole
            }

            with open("vala_dataset.jsonl", "a") as f:
                f.write(json.dumps(data) + "\n")
            
            break

def is_valid_line(line):
    return line.strip() and not line.strip().startswith(("//", "{", "```", "public class"))

def is_valid_hole(hole):
    return hole not in ("{", "}") and not hole.startswith(("*", "/", "public class"))

def process_response_llm(snippet):
    for attempts in range(3):
        prompt = """In the following Vala code, write out a snippet from the code that could be predicted by a language model. The snippet should be no more than a few lines long and should accurately reproduce a part of the code provided, including precisely replicating any whitespace and formatting. Write the snippet and your justification for the snippet.
**Code**

"""

        example_code = """
    public class HelloWorld : Object {
        public static int main(string[] args) {
            stdout.printf("Hello, World!\n");
            return 0;
        }
    }
"""

        example_response = """
**Justification**
The code provided is a simple Vala program that prints "Hello, World!" to the console. This is a very common exampled used to demonstrate the syntax of a new programming language. I will select a snippet that includes the print statement and the return statement, as these are essential parts of the program and are likely to be predicted by a language model. I'll begin my snippet after the print statement to provide context for the prediction.

**Snippet**
```vala
("Hello, World!\n");
            return 0;
        }
    }
```

    """

        example_code_2 = """
        row_activated.connect((path, column) => {
            row_clicked(int.parse(path.to_string()));
        });
        n_rows = 0;
    }

    public void add_row(string[] vals) {
        Gtk.TreeIter iter;
        liststore.append(out iter);
        for(int i = 0; i < vals.length; i++) {
            liststore.set_value(iter, i, vals[i]);
        }
        n_rows++;
    }
"""

        example_response_2 = """
**Justification**
The snippet is a part of the provided code that adds a row to a list store in a GTK application. I will select a snippet that includes the for loop that iterates over the values to set them in the list store. This snippet is a common pattern in GTK applications for adding data to a list store. I'll begin my snippet after the for keyword as it is necessary to provide context to predict the snippet.

**Snippet**
```vala
int i = 0; i < vals.length; i++) {
            liststore.set_value(iter, i, vals[i]);
        }
        n_rows++;
    }
```

    """

        example_code_3 = """
var point_b = new Point.degrees(0, 0);
var point_a = new Point.degrees(0, 0);

foreach (var p in points) {
    point_a = point_b;
    point_b = p;

    if (count >= 1) {
        ret += Math.acos(Math.sin(point_a.rlat) * Math.sin(point_b.rlat)
                + Math.cos(point_a.rlat) * Math.cos(point_b.rlat) * Math.cos(point_b.rlon - point_a.rlon)) * 6371109; //the mean radius of earth
        count++;
    }
}

return ret;

/**
 * Sets the colour and alpha (transparency) of the track.
 * All values should be between 0 and 1.0. Zero is black/transparent.
 * 1.0 is white/not transparent.
 */
public void set_color(double r, double g, double b, double a) {
    color.red = r;
    color.blue = b;
    color.green = g;
    color.alpha = a;
}

/**
 * Gets the RGBA values for the track color.
 */
public void get_color(out double r, out double g, out double b, out double a) {
    r = color.red;
    g = color.green;
    b = color.blue;
}
"""
        example_response_3 = """
    **Justification**
    The snippet shows a partial implementation of a function that calculates the distance between two points on the Earth's surface using the Haversine formula. This is a common calculation used in geospatial applications. I will not select a snippet from this function as there is not a clear starting point for the snippet that would make sense out of context. There are two functions defined after the distance calculation function that set and get the color of a track. I will select a snippet from the set_color function as there is a predictable pattern in setting the color values. I'll begin my snippet after the function signature to provide context for the prediction.

    **Snippet**
```vala
    color.red = r;
    color.blue = b;
    color.green = g;
    color.alpha = a;
}
```

    """

        print(snippet)

        response = tryMessages([
            {"role": "system", "content": "You are a language model assistant."},
            {"role": "user", "content": prompt + example_code},
            {"role": "assistant", "content": example_response},
            {"role": "user", "content": prompt + example_code_2},
            {"role": "assistant", "content": example_response_2},
            {"role": "user", "content": prompt + example_code_3},
            {"role": "assistant", "content": example_response_3},
            {"role": "user", "content": prompt + snippet}
        ])

        # extract the snippet from the response (denoted by ```vala and ```)
        try:
            output = response.split("```vala")[1].split("```")[0].strip()
        except IndexError:
            continue

        # check if the output exists in the snippet
        if output in snippet:
            # replace the snippet with the hole placeholder
            snippet = snippet.replace(output, "<|fim_hole|>")
            data = {
                "instruction": snippet,
                "output": output
            }

            with open("vala_dataset.jsonl", "a") as f:
                f.write(json.dumps(data) + "\n")
            
            break

def clone_repositories(repo_names):
    for repo_name in repo_names:
        command = f"git clone {repo_name} repos/{repo_name.split('/')[-1]}"
        os.system(command)

def get_vala_files(repo_name):
    vala_files = []
    for root, _, files in os.walk(f"repos/{repo_name.split('/')[-1]}"):
        for file in files:
            if file.endswith(".vala"):
                vala_files.append(os.path.join(root, file))
    return vala_files

def main():
    with open("repositories.txt", "r") as f:
        repo_names = f.read().splitlines()

    clone_repositories(repo_names)

    count = 0
    do_odd_numbers = False
    for repo_name in repo_names:
        count += 1
        if do_odd_numbers and count % 2 == 0:
            continue
        if not do_odd_numbers and count % 2 != 0:
            continue
        
        if(repo_name.startswith("#")):
            continue

        vala_files = get_vala_files(repo_name)
        
        for vala_file in vala_files:
            print("Processing file:", vala_file)
            process_file(vala_file)

if __name__ == "__main__":
    main()

