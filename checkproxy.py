import requests

proxies={
    'http': 'http://jawad024:ZsvM_sKT=UN7zxg@pr.oxylabs.io:7777',
    'https': 'http://jawad024:ZsvM_sKT=UN7zxg@pr.oxylabs.io:7777',
}
response = requests.get('https://ip.oxylabs.io/location', proxies=proxies)
print(response.text)