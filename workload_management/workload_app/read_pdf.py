import pymupdf # imports the pymupdf library
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

