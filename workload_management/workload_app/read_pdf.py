import pymupdf # imports the pymupdf library
import math

doc = pymupdf.open("course_report.pdf") # open a document
text = ''
for page in doc: # iterate the document pages
  text += page.get_text() # get plain text encoded as UTF-8


end = text.find('WHAT I LIKE')
start = text.find('COURSE LEARNING OUTCOMES')

extracted = text[start:end]
extracted_list = extracted.split('\n')

all_mlo_data = []

response_count_pos = extracted_list.index('Response Count')
while(response_count_pos < len(extracted_list)):

    mlo_item = {
        'response_count' : 0,
        'mean' : 0,
        'standard_deviation' : 0
        }
    try:
        new_list = extracted_list[response_count_pos:response_count_pos+10]
        new_response_count_pos = new_list.index('Response Count')
        mlo_item['response_count'] = new_list[new_response_count_pos+1]
        mlo_item['mean'] = new_list[new_response_count_pos+3]
        mlo_item['standard_deviation'] = new_list[new_response_count_pos+5]
        all_mlo_data.append(mlo_item)
        response_count_pos += 10
    except:
        break

print(all_mlo_data)

item = all_mlo_data[0]

resp_cnt = int(item['response_count'])
avg = float(item['mean'])
std = float(item['standard_deviation'])

distributions = []
for n_four in range(0,resp_cnt-4):
    for n_three in range(0,resp_cnt-4):
        for n_two in range(0,resp_cnt-4):
            n_one = resp_cnt - n_four-n_three-n_two
            calc_mean = (n_four*4+n_three*3+n_two*2+n_one)/resp_cnt
            calc_std = math.sqrt((n_four*(4 - calc_mean)**2 + n_three*(3 - calc_mean)**2 +\
                       n_two*(2-calc_mean)**2 + (n_one - calc_mean)**2)/resp_cnt)
            #print(calc_std)
            if (abs(calc_mean - avg) < 0.05 and abs(calc_std - std) < 0.05):
                dist = {
                    'fours' : n_four,
                    'threes' : n_three,
                    'twos' : n_two,
                    'ones' : n_one,
                    'avg' :  calc_mean,
                    'std' : calc_std
                    }
                distributions.append(dist)
print(len(distributions))
            
            
            