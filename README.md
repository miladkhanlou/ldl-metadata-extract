# Overview of the pipeline:
1. **Institution level data(Optional):** Extract all collections within an institution.
    - `PID` of the collection
    - Collection `Content model`
    - Collection `Description`
    - Collection `Title`
2. **Information of All content within Collection**: Extract data about objects
    - `PIDs` of objects
    - `Content model`
    - `parent_PID`(parent page)
    - `title`(title of the page).
3. **Run bash scripts to extract datastream metadata**
    - `PID` the object
    - `filetype`
    - `file_size`
    - `file_path`
   - `institution`
    - `collection_name`
    - `mods_path`
    - `rdf_path`
4. **Merge and process (final accounting csv):** Merge all data and process the result to a final csv.
    - `PID`
    - `Content model`
    - `Title`
    - `filetype`
    - `file_size`
    - `institution`
    - `collection_name`
    - `file_path`
    - `mods_path`
    - `rdf_path`
    
---
# Step-by-Step Instructions for Extracting, Processing, and Organizing Metadata from LDL Collections
## Step 1: Extract all collections within an institution.
**Objective:** Retrieve all Collection data within a specific collection.

Includes the following data:
- `PID`, `content_model`, `Description`, and `title`.

***Note:*** We need to change institution name in the query bellow.
  - Before ``FILTER REGEX(STR(?pid), "louisiananewspapers-")``
  - After ``FILTER REGEX(STR(?pid), "lsu-")``

```sparql
PREFIX fedora: <info:fedora/fedora-system:def/model#>
PREFIX view: <info:fedora/fedora-system:def/view#>
PREFIX rel: <info:fedora/fedora-system:def/relations-external#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX premis: <http://www.loc.gov/premis/rdf/v1#>

SELECT DISTINCT 
    (REPLACE(STR(?pid), "^info:fedora/", "") AS ?PID)
    ?collection_name
    ?collection_Description
    (STRAFTER(STR(?collection_pid), "info:fedora/islandora:") AS ?parent)
WHERE {
  ?pid fedora:hasModel ?contentModel .
  ?pid rel:isMemberOfCollection ?collection_pid .
  
  # Filter To get all collections
  FILTER REGEX(STR(?contentModel), "fedora/islandora:collectionCModel")

  # Filter for the desired namespace
  FILTER REGEX(STR(?pid), "louisiananewspapers-")
  
  # Retrieve additional metadata
  OPTIONAL { ?pid fedora:label ?collection_name . }
  OPTIONAL { ?pid dc:description ?collection_Description. }
}
```
## Step 2: Extract data about objects:
**Objective:** Retrieve all `PID`s within a specific collection, including hierarchical relationships.

**SPARQL Query:**
Run a comprehensive query for a specific collection, such as `info:fedora/lsu-ag-agexp:collection`. The query should extract:
- Direct members of the collection
- Compound objects
- Children of compound objects
- Newspaper issues, pages, and any nested relationships

Includes the following data:
- `PID`, `content_model`, `parent_PID`, and `title`.

***Note:*** We need to change `collection name` in the query bellow.
  - Before ``<info:fedora/louisiananewspapers-orleans:collection>``
  - After ``<info:fedora/lsu-sc-ajleblanc:collection>``

Saves the output to `all_pids.csv` in this git repository folder.
```sparql
PREFIX fedora: <info:fedora/fedora-system:def/model#>
PREFIX view: <info:fedora/fedora-system:def/view#>
PREFIX rel: <info:fedora/fedora-system:def/relations-external#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX premis: <http://www.loc.gov/premis/rdf/v1#>

SELECT DISTINCT 
    (REPLACE(STR(?pid), "^info:fedora/", "") AS ?PID)
    (STRAFTER(STR(?contentModel), "info:fedora/islandora:") AS ?content_model)
    ?title
    (REPLACE(STR(?parent_pid), "^info:fedora/", "") AS ?parent_PID)
WHERE {
  {
    # PIDs directly in the collection
    ?pid rel:isMemberOfCollection <info:fedora/louisiananewspapers-orleans:collection> .
    OPTIONAL { ?pid fedora:label ?title . }
    OPTIONAL { ?pid fedora:hasModel ?contentModel . }
    BIND(<info:fedora/louisiananewspapers-orleans:collection> AS ?parent_pid)
  }
  UNION
  {
    # Children of compounds in the collection
    ?pid rel:isMemberOf ?compound .
    ?compound rel:isMemberOfCollection <info:fedora/louisiananewspapers-orleans:collection> .
    OPTIONAL { ?pid fedora:label ?title . }
    OPTIONAL { ?pid fedora:hasModel ?contentModel . }
    BIND(?compound AS ?parent_pid)
  }
  UNION
  {
    # Objects within compounds
    ?pid rel:isConstituentOf ?compound .
    ?compound rel:isMemberOfCollection <info:fedora/louisiananewspapers-orleans:collection> .
    OPTIONAL { ?pid fedora:label ?title . }
    OPTIONAL { ?pid fedora:hasModel ?contentModel . }
    BIND(?compound AS ?parent_pid)
  }
  UNION
  {
    # Newspaper content models within issues
    ?pid rel:isMemberOf ?newspaperIssue .
    ?newspaperIssue rel:isMemberOf ?compound .
    ?compound rel:isMemberOfCollection <info:fedora/louisiananewspapers-orleans:collection> .
    OPTIONAL { ?pid fedora:label ?title . }
    OPTIONAL { ?pid fedora:hasModel ?contentModel . }
    BIND(?newspaperIssue AS ?parent_pid)
  }
  UNION
  {
    # Objects within final newspaper content model
    ?pid rel:isConstituentOf ?compoundnewspaper .
    ?compoundnewspaper rel:isMemberOf ?newspaperIssue .
    ?newspaperIssue rel:isMemberOf ?compound .
    ?compound rel:isMemberOfCollection <info:fedora/louisiananewspapers-orleans:collection> .
    OPTIONAL { ?pid fedora:label ?title . }
    OPTIONAL {
      ?pid fedora:hasModel ?contentModel .
      FILTER STRSTARTS(STR(?contentModel), "info:fedora/islandora:")  
    }
    BIND(?compoundnewspaper AS ?parent_pid)
  }
  FILTER STRSTARTS(STR(?contentModel), "info:fedora/islandora:")
}
```
## Step 3: Extract PDF and OBJ Datastreams:
**Objective:** Retrieve all PIDs with PDF and OBJ data streams within the collection.

**Bash Script:** Run bash scripts on the Fedora datastream storage location (`/data/fedoraData/datastreamStore`)

Download the output CSVs in this git repository folder.
- `datastreams-pdf.csv` for PDF data streams
- `datastreams-obj.csv` for OBJ data streams

**Expected Output:**
CSVs for PDF and OBJ data streams, including:
- `PID`, `filetype`, `file_size`, `file_path`, `mods_path`, `rdf_path`.
```sh
#!/bin/bash
date
headers="PID,filetype,PDF Size,Institution,collection_name,PDF Path,MODS Path,RELS-EXT Path"
echo -e $headers > "/tmp/outfiles/milad/datastream-pdf.csv"

for dir in $(ls -d ../../datastreamStore/*); do
  echo $dir
  for file in "$dir"/*{COLLECTION_NAME}*PDF*.0; do
    if [[ -f "$file" ]]; then
      echo $file
      PID=$(echo -e "${file}" | sed 's/info%3Afedora%2F//g' | grep -o "[a-zA-Z0-9-]*%3A[0-9a-zA-Z]*" | sed 's/%3A/:/g')
      collection="$(echo $PID | cut -d ':' -f 1):collection"
      institution=$(echo $PID | cut -d '-' -f 1)
      filetype=$(file -b --mime-type "$file")
      PDF_Size=$(stat --format="%s" "$file")
      PDF_path="https://louisianadigitallibrary.org/islandora/object/${PID}/datastream/PDF/download"
      mods_path="https://louisianadigitallibrary.org/islandora/object/${PID}/datastream/MODS/download"
      relsext_path="https://louisianadigitallibrary.org/islandora/object/${PID}/datastream/RELS-EXT/download"
      line="${PID},${filetype},${PDF_Size},${institution},${collection},${PDF_path},${mods_path},${relsext_path}"
      echo -e $line >> "/tmp/outfiles/milad/datastream-pdf.csv"
    fi
  done
done
date
```
## Step 3: Merge and Update Metadata

**Objective:** Merge the `PDF` and `OBJ` data streams with the comprehensive PIDs metadata (`collection_all_pids.csv`).

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
Run `merge_and_process.py` to create final accounting as single output.

## Step 4: Post-Processing

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

## Step 5: Save and Organize Files

**Objective:** Save all outputs to a dedicated location for the collection.

**Process:**
Copy all relevant CSVs (`all_collections.csv`, `lsu_collections.csv`, `collection_all_pids.csv`, `collection_pdf_pids.csv`, `collection_obj_pids.csv`, `collection_merged_metadata.csv`, `collection_final_metadata.csv`) to the designated L drive or repository.

**Expected Output:**
A structured and organized folder with all data and metadata for the collection.
