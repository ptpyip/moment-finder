import json
import os.path

def load_jsonl(file_path):
    with open(file_path, "rb") as f:
        for line in f.readlines():
            yield json.loads(line)
            
def write_jsonl(dict_list, out_dir, file_name):
     with open(os.path.join(out_dir, f"{file_name}.jsonl"), 'w') as out:
        for data in dict_list:
            josn_data = json.dumps(data) + '\n'
            out.write(josn_data)
           