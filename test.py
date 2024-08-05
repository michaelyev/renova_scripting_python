items = [
    {'color_name': '#ded6cc', 'model': 'kohler-28000-cm1'},
    {'color_name': '#000000', 'model': 'kohler-2209-7'},
    {'color_name': '#ffffff', 'model': 'kohler-2209-0'}
]

target = 'K-28000-cm1'
target_suffix = '-'.join(target.split('-')[1:])  # Extract the suffix part (2209-0)

match = next((item for item in items if '-'.join(item['model'].split('-')[1:]) == target_suffix), None)

if match:
    print('Matched item:', match)
else:
    print('No match found')
