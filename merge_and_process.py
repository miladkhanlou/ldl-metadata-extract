import pandas as pd

# Global Variables, CSV file names
updated_all_pids= "PID_all_pids_with_relationships.csv"
pdf_datastream_pids = "datastream-data-pdf.csv"
obj_datastream_pids = "datastream-data-obj.csv"
mods_datastream_pids = "datastream-data-mods.csv"

# Global functions, Get PID and output directory
def get_pid_name(all_pids):
    all_pids = pd.read_csv(all_pids)
    PID = all_pids["PID"][0].split(":")[0]
    return PID

def outpud_dir(PID):
    output_file = f"full-{PID}-output.csv"
    return output_file

def merge_data(pids, pdfs, objs, mods, PID):
    # Load CSVs
    all_pids = pd.read_csv(pids)
    pdf_pids = pd.read_csv(pdfs)
    obj_pids = pd.read_csv(objs)
    mods_pids = pd.read_csv(mods)
    
    # standalize column names:
    pdf_pids.columns = ["PID", "filetype", "file_size",  "institution", "Collection_name", "file_path", "mods_path", "rdf_path"]
    obj_pids.columns = ["PID", "filetype", "file_size","institution", "Collection_name", "file_path", "mods_path", "rdf_path"]
    mods_pids.columns = ["PID", "filetype", "file_size","institution", "Collection_name", "file_path", "mods_path", "rdf_path"]
    
    # Create lookup dictionaries for PDF and OBJ
    pdf_lookup = pdf_pids.set_index("PID")[["filetype", "file_size",  "institution", "Collection_name", "file_path", "mods_path", "rdf_path"]].to_dict(orient="index")
    obj_lookup = obj_pids.set_index("PID")[["filetype", "file_size",  "institution", "Collection_name", "file_path", "mods_path", "rdf_path"]].to_dict(orient="index")
    mods_lookup = mods_pids.set_index("PID")[["filetype", "file_size",  "institution", "Collection_name", "file_path", "mods_path", "rdf_path"]].to_dict(orient="index")

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
            print(pdf_row)
            output_rows.append(pdf_row)

        # Check for OBJ data
        if pid in obj_lookup:
            obj_row = base_row.copy()
            obj_row.update(obj_lookup[pid])  # Add OBJ data to the row
            output_rows.append(obj_row)
            
        # Check for OBJ data
        if pid in mods_lookup:
            obj_row = base_row.copy()
            obj_row.update(mods_lookup[pid])  # Add mods data to the row
            output_rows.append(obj_row)

        # If no PDF or OBJ, keep the original row
        if pid not in pdf_lookup and pid not in obj_lookup and pid not in mods_lookup:
            output_rows.append(base_row)

    # Create a DataFrame from the output rows
    final_df = pd.DataFrame(output_rows)
    print(final_df)
    return final_df

def to_csv(final_df, output_file):
    # Save the final output
    final_df.to_csv(output_file, index=False)
    print(f"Final Accounting saved as {output_file}")

def post_process_data(raw_data):
    output_rows = []
    csv = pd.read_csv(raw_data)
    for _, row in csv.iterrows():
        base_row = row.to_dict()
        content_model = base_row["content_model"]
        if content_model != "newspaperIssueCModel" and content_model != "sp_large_image_cmodel" and content_model != "sp-audioCmodel" and content_model != "sp_videoCmodel" and content_model != "sp_remote_resource" :
            base_row["filetype"] = ""
            base_row["file_size"] = ""
            base_row["file_path"] = ""
        else:
            base_row["file_size"] = f"{base_row['file_size'] / 1000}"
        output_rows.append(base_row)
    # Create a DataFrame from the output rows
    processed_df = pd.DataFrame(output_rows)
    return processed_df        

def merge():
    PID = get_pid_name(updated_all_pids)
    output = outpud_dir(PID)
    merged_df = merge_data(updated_all_pids, pdf_datastream_pids, obj_datastream_pids, mods_datastream_pids, PID)
    to_csv(merged_df, f"pre-processed-{output}")

def post_process():
    PID = get_pid_name(updated_all_pids)
    output = outpud_dir(PID)
    post_processed_df = post_process_data(f"pre-processed-{output}")
    to_csv(post_processed_df, f"processed-{output}")
    
if __name__ == "__main__":      
    # merge()
    post_process()
    
    
