import pandas as pd

# Global Variables, CSV file names
updated_all_pids= "all-pids.csv"
pdf_datastream_pids = "datastream-pdf.csv"
obj_datastream_pids = "datastream-obj.csv"

# Global functions, Get PID and output directory
def get_pid_name(all_pids):
    all_pids = pd.read_csv(all_pids)
    PID = all_pids["PID"][0].split(":")[0]
    return PID

def outpud_dir(PID):
    output_file = f"full-{PID}.csv"
    return output_file

def merge_data(all_pids, pdf_pids, obj_pids, PID):
    # Load CSVs
    all_pids = pd.read_csv(all_pids)
    pdf_pids = pd.read_csv(pdf_pids)
    obj_pids = pd.read_csv(obj_pids)
    

    # standalize column names:
    pdf_pids.columns = ["PID", "filetype", "file_size", "file_path",  "mods_path", "rdf_path", "institution", "Collection_name"]
    obj_pids.columns = ["PID", "filetype", "file_size", "file_path",  "mods_path", "rdf_path", "institution", "Collection_name"]


    # Create lookup dictionaries for PDF and OBJ
    pdf_lookup = pdf_pids.set_index("PID")[["filetype", "file_size", "file_path",  "mods_path", "rdf_path", "institution", "Collection_name"]].to_dict(orient="index")
    obj_lookup = obj_pids.set_index("PID")[["filetype", "file_size", "file_path",  "mods_path", "rdf_path", "institution", "Collection_name"]].to_dict(orient="index")

    # Create an output list to store rows
    output_rows = []

    # Process each row in the updated PIDs CSV
    for _, row in all_pids.iterrows():
        pid = row["PID"]
        base_row = row.to_dict()  # Convert the row to a dictionary for modification
        
        # Check for PDF data
        if pid in pdf_lookup:
            pdf_row = base_row.copy()
            pdf_row.update(pdf_lookup[pid])  # Add PDF data to the row
            # print(pdf_row)
            output_rows.append(pdf_row)

        # Check for OBJ data
        if pid in obj_lookup:
            obj_row = base_row.copy()
            obj_row.update(obj_lookup[pid])  # Add OBJ data to the row
            output_rows.append(obj_row)

        # If no PDF or OBJ, keep the original row
        if pid not in pdf_lookup and pid not in obj_lookup:
            output_rows.append(base_row)

    # Create a DataFrame from the output rows
    final_df = pd.DataFrame(output_rows)
    return final_df

def to_csv(final_df, output_file):
    # Save the final output
    final_df.to_csv(output_file, index=False)

def filter_datastreams(raw_data):
    output_rows = []
    csv = pd.read_csv(raw_data)
    for _, row in csv.iterrows():
        base_row = row.to_dict()
        parent_pid_name = base_row["parent_PID"]
        pid_name = base_row["PID"]
        content_model = base_row["content_model"]
        
        if content_model != "newspaperIssueCModel" and content_model != "sp_large_image_cmodel" and content_model != "sp-audioCmodel" and content_model != "sp_videoCmodel" and content_model != "sp_remote_resource"  and content_model != "sp_pdf" and content_model != "sp-ohCModel":
            base_row["filetype"] = ""
            base_row["file_size"] = ""
            base_row["file_path"] = ""
            
        else:
            base_row["file_size"] = f"{base_row['file_size'] / 1000}Kb"
            
        # fill out data from collection objects:
        if "collection" in parent_pid_name: # create MODS and RDF path for collection PIDs
            base_row["mods_path"] = f"https://louisianadigitallibrary.org/islandora/object/{pid_name}/datastream/MODS/download"
            base_row["rdf_path"] = f"https://louisianadigitallibrary.org/islandora/object/{pid_name}/datastream/RELS-EXT/download"
            base_row["institution"] = pid_name.split("-")[0]
            base_row["Collection_name"] = f"{pid_name.split(':')[0]}:collection"
            
        output_rows.append(base_row)
        
    # Create a DataFrame from the output rows
    processed_df = pd.DataFrame(output_rows)
    return processed_df 

def post_process(df):
    # Identify rows that filetype is is empty:
    rows_to_drop = df[(df.duplicated(subset=['PID'], keep='first')) & (df['filetype'] == "")]
    
    # Drop the identified rows
    cleaned_df = df[~((df.duplicated(subset=['PID'], keep='first')) & (df['filetype'] == ""))]
    return cleaned_df
    
def merge():
    PID = get_pid_name(updated_all_pids)
    output = outpud_dir(PID)
    merged_df = merge_data(updated_all_pids, pdf_datastream_pids, obj_datastream_pids, PID)
    to_csv(merged_df, f"collections/{PID}/merged-{output}")
    print(f"Merged data saved as output-pre-processed-{output} ...")

def process():
    PID = get_pid_name(updated_all_pids)
    output = outpud_dir(PID)
    datastrean_filter_df = filter_datastreams(f"collections/{PID}/merged-{output}")
    post_processed_df = post_process(datastrean_filter_df) # Process the DataFrame to separate rows to drop and cleaned data
    to_csv(post_processed_df, f"collections/{PID}/{output}") # Save the cleaned DataFrame
    
    print(f"Final Accounting saved as output-processed-{output} ...\n-----------------------------------------------------------------------------------")

if __name__ == "__main__":
    print("Start Merging and Processing Data...\n")   
    merge()
    process()
    
# To test if a row had 2 duplicated rows and we wanted to keep the ones that filetype is not none, in output-pre-processed make changes to the row with both pdf and obj to make pdf row to newspaperIssueCmodel 
    
    
