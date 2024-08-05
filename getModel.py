def extract_filename_from_url(url):
    # Find the position of the last slash
    last_slash_pos = url.rfind('/')
    
    # Extract the part after the last slash
    filename_with_ext = url[last_slash_pos + 1:]
    
    # Remove the file extension
    filename_without_ext = filename_with_ext.rsplit('.', 1)[0]
    
    return filename_without_ext

# Example URL
url = "https://s3.img-b.com/image/private/t_base,c_lpad,f_auto,dpr_auto,w_90,h_90/product/kohler/kohler-k-8206-cm6-3313715.jpg"

# Extract filename
print(extract_filename_from_url(url))
