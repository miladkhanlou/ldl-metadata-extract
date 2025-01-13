# Step-by-Step Instructions for Extracting, Processing, and Organizing Metadata from LDL Collections

## Step 1: Extract Comprehensive Information About All Collections

**Objective:** Retrieve information about all collections within the Louisiana Digital Library (LDL).

**SPARQL Query:**
Run a query to extract all collections within LDL. The query should include the following information for each collection:
- PID of the collection
- Content model
- Description
- Contributor
- Title of the collection

Save the output to a CSV file named `all_collections.csv`.

**Expected Output:**
A CSV with all collections in LDL, containing:
- `PID`, `content_model`, `description`, `contributor`, and `title`.

## Step 2: Extract Collections for a Specific Institution

**Objective:** Retrieve collections specific to an institution namespace (e.g., LSU) with additional detailed information about the collection.

**SPARQL Query:**
Modify the previous query to filter by the institution namespace (e.g., LSU). Extract detailed information for each collection within the institution, including:
- PID of the collection
- Content model
- Description
- Contributor
- Title of the collection

Save the output to `lsu_collections.csv`.

**Expected Output:**
A CSV with all collections under LSU, containing:
- `PID`, `content_model`, `description`, `contributor`, and `title`.

## Step 3: Extract All PIDs Within a Specific Collection

**Objective:** Retrieve all PIDs within a specific collection, including hierarchical relationships.

**SPARQL Query:**
Run a comprehensive query for a specific collection, such as `info:fedora/lsu-ag-agexp:collection`. The query should extract:
- Direct members of the collection
- Compound objects
- Children of compound objects
- Newspaper issues, pages, and any nested relationships

Include the following fields:
- `PID`, `content_model`, `parent_PID`, and `title`.

Save the output to `collection_all_pids.csv`.

**Expected Output:**
A CSV with all PIDs in the collection, including hierarchical relationships and metadata:
- `PID`, `content_model`, `parent_PID`, and `title`.

## Step 4: Extract PDF and OBJ Data Streams

**Objective:** Retrieve all PIDs with PDF and OBJ data streams within the collection.

**Bash Script:**
Run a script on the Fedora data stream storage location for the collection namespace. Specify the data stream type (PDF or OBJ).

Save the output to separate CSVs:
- `collection_pdf_pids.csv` for PDF data streams
- `collection_obj_pids.csv` for OBJ data streams

**Expected Output:**
CSVs for PDF and OBJ data streams, including:
- `PID`, `filetype`, `file_size`, `file_path`, `mods_path`, `relzx_path`.

## Step 5: Merge and Update Metadata

**Objective:** Merge the PDF and OBJ data streams with the comprehensive PIDs metadata (`collection_all_pids.csv`).

**Python Script:**
Use the merge function in the Python script to:
- Update the comprehensive PIDs CSV with metadata from PDF and OBJ CSVs.
- For each PID, add:
  - `filetype`, `file_size`, `file_path`, `mods_path`, and `relzx_path`.
- Handle cases where a PID has both PDF and OBJ by creating separate rows for each.

Save the updated file as `collection_merged_metadata.csv`.

**Expected Output:**
A merged CSV containing all PIDs, their hierarchical relationships, and metadata for PDF and OBJ data streams:
- `PID`, `content_model`, `title`, `parent_PID`, `filetype`, `file_size`, `file_path`, `mods_path`, `relzx_path`.

## Step 6: Post-Processing

**Objective:** Clean and finalize the merged CSV to ensure only relevant data is retained and formatted correctly.

**Post-Processing Steps:**
1. **Filter Out Unnecessary Rows:**
   - Retain metadata for PDF data streams only if the `content_model` is `newspaperIssue`.
   - Clear `file_size`, `file_path`, `mods_path`, and `relzx_path` for rows where `content_model` is not `newspaperIssue`.
2. **Format File Size:**
   - Convert `file_size` from bytes to kilobytes (divide by 1024).
3. **Finalize CSV:**
   - Ensure all rows are updated and ready for export.

Save the final file as `collection_final_metadata.csv`.

**Expected Output:**
A cleaned and finalized CSV containing:
- `PID`, `content_model`, `title`, `parent_PID`, `filetype`, `file_size (KB)`, `file_path`, `mods_path`, `relzx_path`.

## Step 7: Save and Organize Files

**Objective:** Save all outputs to a dedicated location for the collection.

**Process:**
Copy all relevant CSVs (`all_collections.csv`, `lsu_collections.csv`, `collection_all_pids.csv`, `collection_pdf_pids.csv`, `collection_obj_pids.csv`, `collection_merged_metadata.csv`, `collection_final_metadata.csv`) to the designated L drive or repository.

**Expected Output:**
A structured and organized folder with all data and metadata for the collection.
