# To get interview container, get element where data-test="InterviewList"
# Valid divs are the ones where data-test starts with "Interview......"
# Do class="col-12" to get main body of interview item
# body_div.select('.mb-xxsm')[3].text gives you the difficulty of the interview
# body_div.select(':nth-child(4) p')[2].text gives you the interview review itself

import glob
import json
import os
import requests
import time
from tqdm import trange
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like'
                         ' Gecko) Chrome/99.0.4844.74 Safari/537.36'}
folder_name = 'microsoft_training_data'
output_name = 'microsoft.json'
start_i = 749
end_i = 1245
url_prefix = 'https://www.glassdoor.com/Interview/Microsoft-Interview-Questions-E1651'


os.makedirs(folder_name, exist_ok=True)
print('')
for i in trange(start_i, end_i, initial=start_i, smoothing=0):
    url = f'{url_prefix}_P{i}.htm'
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        print('Connection error. Retrying...')
        time.sleep(60)
        r = requests.get(url, headers=headers)
    html = BeautifulSoup(r.text, features="html.parser")
    interview_container = html.find(attrs={'data-test': 'InterviewList'})
    review_list = []
    for child in interview_container.children:
        if child.get('data-test') is not None and child.get('data-test').startswith('Interview'):
            main_body = child.select_one('.col-12')
            interview_checkpoints = main_body.select('.mb-xxsm')
            if len(interview_checkpoints) == 4:
                offer_status = interview_checkpoints[1].text
                experience = interview_checkpoints[2].text
                difficulty = interview_checkpoints[3].text
            else:
                continue
            p_divs = main_body.select(':nth-child(4) p')
            if len(p_divs) == 3:
                review = p_divs[2].text
            else:
                continue
            review_list.append({'offer_status': offer_status, 'experience': experience,
                                'difficulty': difficulty, 'review': review, 'page': i})
    with open(f'{folder_name}/P{i}.json', 'w') as f:
        json.dump(review_list, f, indent=2)

full_training_json = []
for file in glob.glob(f'{folder_name}/P*'):
    with open(file) as f:
        full_training_json += json.load(f)
with open(f'{folder_name}/{output_name}', 'w') as f:
    json.dump(full_training_json, f, indent=2)
print('done!')
