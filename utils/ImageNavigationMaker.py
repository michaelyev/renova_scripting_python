def extract_filename_from_url(url):
    # Find the position of the last slash
    last_slash_pos = url.rfind('/')
    
    # Extract the part after the last slash
    filename_with_ext = url[last_slash_pos + 1:]
    
    # Remove the file extension
    filename_without_ext = filename_with_ext.rsplit('.', 1)[0]
    
    return filename_without_ext
