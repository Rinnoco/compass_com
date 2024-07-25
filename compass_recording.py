import os
import zipfile
import time
import tempfile


def compress_and_record_size(inp_file_name, out_zip_file, label, compression=zipfile.ZIP_BZIP2, out_file='results.csv',
                             cluster_id=0):
    """
    function : file_compress
    args : inp_file_names : list of filenames to be zipped
    out_zip_file : output zip file
    return : none
    assumption : Input file paths and this code is in same directory.
    """

    print(f" *** Input File name passed for zipping - {inp_file_name}")

    zip_extension = {zipfile.ZIP_DEFLATED: ".gzip.zip", zipfile.ZIP_BZIP2: ".bzip2.zip", zipfile.ZIP_LZMA: ".lzma.zip"}
    out_zip_file = out_zip_file + zip_extension[compression]
    # create the zip file first parameter path/name, second mode
    print(f' *** out_zip_file is - {out_zip_file}')
    zf = zipfile.ZipFile(out_zip_file, mode="w")

    start_compress_time = time.time()  # Start time for compression
    try:
        # Add file to the zip file
        # first parameter file to zip, second filename in zip
        print(f' *** {label}: Processing file {inp_file_name}')
        zf.write(inp_file_name, out_zip_file, compress_type=compression)
    except FileNotFoundError as e:
        print(f' *** Exception occurred during zip process - {e}')
    finally:
        # Don't forget to close the file!
        zf.close()
    compress_time = time.time() - start_compress_time  # End time for compression

    size = os.path.getsize(out_zip_file)

    # Measure decompression time
    start_decompress_time = time.time()
    with zipfile.ZipFile(out_zip_file, 'r') as zip_ref:
        zip_ref.extractall(tempfile.mkdtemp())
    decompress_time = time.time() - start_decompress_time

    with open(out_file, "a") as f:
        f.write(f"{cluster_id},{os.path.basename(inp_file_name)},{label},{zip_extension[compression]},{size},bytes,{compress_time},s,{decompress_time},s\n")
    os.remove(out_zip_file)
