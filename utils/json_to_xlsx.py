import sys; sys.path.insert(0, "..")
import utils.file_io as file_io
import json
import pandas as pd

with open(sys.argv[1]) as json_file:
    data = json.load(json_file)

final_df = pd.read_json(json.dumps(data))

file_io.write_xlsx(final_df, sys.argv[2])
