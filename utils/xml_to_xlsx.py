import sys; sys.path.insert(0, "..")
import utils.file_io as file_io
import xml.etree.ElementTree as ET
import pandas as pd

xml_data = open(sys.argv[1]).read()

#def xml2df(xml_data):
root = ET.XML(xml_data) # element tree
all_records = []
for i, child in enumerate(root):
    record = {}
    for subchild in child:
        record[subchild.tag] = subchild.text
        all_records.append(record)

df = pd.DataFrame(all_records)
df = df.dropna(axis=1,how='all')
final_df = df.drop_duplicates(keep = 'first')

file_io.write_xlsx(final_df, sys.argv[2])
