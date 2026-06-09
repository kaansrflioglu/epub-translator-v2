import os
import re

def natural_sort_key(s):
    """Sort strings containing numbers in human/natural order."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def get_html_files(directory):
    """Lists and naturally sorts HTML files in a given directory."""
    if not os.path.exists(directory):
        return []
    
    files = [
        f for f in os.listdir(directory) 
        if f.lower().endswith(('.html', '.xhtml', '.htm'))
    ]
    files.sort(key=natural_sort_key)
    return files

def read_file_content(file_path):
    """Reads text content from a file using UTF-8 encoding."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def ensure_directory_exists(directory):
    """Creates a directory if it does not already exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_txt_files(directory):
    """Lists and naturally sorts TXT files in a given directory."""
    if not os.path.exists(directory):
        return []

    files = [
        f for f in os.listdir(directory)
        if f.lower().endswith('.txt')
    ]
    files.sort(key=natural_sort_key)
    return files

def get_next_output_path(outputs_dir, base_name="combined_text", extension=".txt"):
    """Determines the next non-conflicting output file path in the outputs directory."""
    ensure_directory_exists(outputs_dir)
    
    # Check baseline: combined_text.txt
    target_path = os.path.join(outputs_dir, f"{base_name}{extension}")
    if not os.path.exists(target_path):
        return target_path
    
    # Try combined_text_2.txt, combined_text_3.txt...
    counter = 2
    while True:
        target_path = os.path.join(outputs_dir, f"{base_name}_{counter}{extension}")
        if not os.path.exists(target_path):
            return target_path
        counter += 1


def extract_epub_html(epub_path, target_dir, clear_target=True):
    """
    Unzips EPUB's HTML/XHTML/HTM documents and extracts them sequentially 
    to the target directory. 
    It parses the EPUB spine (reading order) and names files with sequential 
    prefixes to preserve reading order for natural sorting.
    """
    import zipfile
    import xml.etree.ElementTree as ET
    import shutil

    if clear_target and os.path.exists(target_dir):
        # Empty the directory contents rather than deleting target_dir itself
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"Warning: could not delete {item_path}: {e}")
                
    ensure_directory_exists(target_dir)

    extracted_files = []
    
    with zipfile.ZipFile(epub_path, 'r') as z:
        # 1. Try to read META-INF/container.xml
        opf_path = None
        try:
            container_data = z.read('META-INF/container.xml')
            root = ET.fromstring(container_data)
            ns = {'ns': 'urn:oasis:names:tc:opendocument:xmlns:container'}
            rootfile = root.find('.//ns:rootfile', ns)
            if rootfile is not None:
                opf_path = rootfile.attrib.get('full-path')
        except Exception as e:
            print(f"Could not parse container.xml: {e}. Falling back to default zip scan.")

        # If we successfully got OPF path, try to parse OPF for spine order
        html_paths_in_order = []
        if opf_path:
            try:
                opf_data = z.read(opf_path)
                opf_root = ET.fromstring(opf_data)
                
                # Get directory of the OPF file inside the zip to resolve relative hrefs
                opf_dir = os.path.dirname(opf_path)
                
                # Parse Manifest: id -> relative href
                manifest = {}
                for item in opf_root.findall('.//{*}item'):
                    item_id = item.attrib.get('id')
                    href = item.attrib.get('href')
                    media_type = item.attrib.get('media-type', '')
                    if item_id and href and ('html' in media_type or href.lower().endswith(('.html', '.xhtml', '.htm'))):
                        manifest[item_id] = href
                
                # Parse Spine for order
                for itemref in opf_root.findall('.//{*}itemref'):
                    idref = itemref.attrib.get('idref')
                    if idref in manifest:
                        href = manifest[idref]
                        # Join path using forward slashes (zip standard uses forward slashes)
                        if opf_dir:
                            full_zip_path = f"{opf_dir}/{href}"
                        else:
                            full_zip_path = href
                        # Normalize path (handling any internal '../' or './')
                        full_zip_path = os.path.normpath(full_zip_path).replace('\\', '/')
                        # Let's verify it actually exists in zip (ignoring case if necessary)
                        namelist = z.namelist()
                        if full_zip_path in namelist:
                            html_paths_in_order.append(full_zip_path)
                        else:
                            # Try to match case-insensitively
                            lower_namelist = {name.lower(): name for name in namelist}
                            if full_zip_path.lower() in lower_namelist:
                                html_paths_in_order.append(lower_namelist[full_zip_path.lower()])
            except Exception as e:
                print(f"Could not parse spine from OPF: {e}. Falling back to default zip scan.")
                html_paths_in_order = []

        # 2. Fallback: if spine parsing failed or returned no files, list all HTML/XHTML/HTM files inside the ZIP
        if not html_paths_in_order:
            all_html = [
                name for name in z.namelist() 
                if name.lower().endswith(('.html', '.xhtml', '.htm'))
            ]
            # Naturally sort them so they are in a reasonable order
            all_html.sort(key=natural_sort_key)
            html_paths_in_order = all_html

        # 3. Extract the files
        # We prefix them with a sequential number to keep them sorted correctly
        pad_width = len(str(len(html_paths_in_order)))
        pad_width = max(pad_width, 4) # at least 4 digits (e.g. 0001)
        
        for index, zip_path in enumerate(html_paths_in_order, start=1):
            try:
                content = z.read(zip_path)
                # Get the original file extension and basename
                base_name = os.path.basename(zip_path)
                name_part, ext = os.path.splitext(base_name)
                
                # Construct new filename, e.g. 0001_cover.xhtml
                new_filename = f"{str(index).zfill(pad_width)}_{name_part}{ext}"
                target_path = os.path.join(target_dir, new_filename)
                
                with open(target_path, 'wb') as f:
                    f.write(content)
                extracted_files.append(new_filename)
            except Exception as e:
                print(f"Error extracting {zip_path}: {e}")
                
    return extracted_files

