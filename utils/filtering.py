def extract_table_values(data):
    result = []

    for entry in data:
        if 'table' in entry and isinstance(entry['table'], dict):
            values = entry['table'].values()
            result.extend(values)
    
    return ' '.join(result)

