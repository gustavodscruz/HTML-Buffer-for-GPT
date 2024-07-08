import re
import os
import shutil
import requests
import pyperclip
import subprocess
from bs4 import BeautifulSoup, NavigableString

api_url = "https://pt.libretranslate.com/translate"

prompt = "Mantenha a estrutura html abaixo e os srcs das imagens(POR FAVOR MANTENHA'src's DAS IMAGENS INTACTADAS, NÃO AS TRADUZA, SENÃO ELAS IRAO QUEBRAR), traduza apenas o conteúdo e alts para inglês, sem fazer resumos ou qualquer coisa assim: \n```html\n"

with open('index.html', 'w', encoding='utf-8') as file:
    html = pyperclip.paste()
    print("Content pasted!")
    file.write(html)
print('Chars before parse:', len(html))


# Crie um objeto BeautifulSoup com o HTML
soup = BeautifulSoup(html, 'html.parser')


for div in soup.find_all('div'):
    div.unwrap()
assert len(soup.find_all('div')) == 0


# Check if all divs are deleted


# Para cada tag no documento
for tag in soup.find_all(True):
    if tag.string:
        tag.string = tag.string.strip()
    # Para cada atributo na tag
    for attr in list(tag.attrs):
        # Se o atributo não for "aria-label", "href", "src" ou "alt", remova-o
        if attr not in ['aria-label', 'href', 'src', 'alt', 'data-src']:
            del tag[attr]
        if attr == 'data-src':
            tag['src'] = tag[attr]
            del tag[attr]
for string in soup.strings:
    
    if isinstance(string, NavigableString) and string.parent == "":
        # Envolve o texto com uma tag <p>
        
        new_tag = soup.new_tag("p")
        new_tag.string = string
        string.replace_with(new_tag)

    # if '&nbsp' in string:
    #     string.replace_with(string.replace('&nbsp;', ' '))

    # if string.find('&nbsp;') != -1:
    #     if string.parent == "":
    #         string.wrap(soup.new_tag('p'))
    #     new_tag = soup.new_tag(string.parent.name)
        
# Atualize a variável html com a versão modificada do HTML
html = str(soup)
print('Chars after parse:', len(html))

htmls = []
buffer = ''
for char in html:
    buffer += char
    if len(buffer) >= 5500 - len(prompt):
        match = re.search(r'<[^>]*>$', buffer)
        if match:
            end = match.start()
            htmls.append(buffer[:end])
            buffer = buffer[end:]
        else:
            last_close_tag = buffer.rfind('>')
            if last_close_tag != -1:
                htmls.append(buffer[:last_close_tag+1])
                buffer = buffer[last_close_tag+1:]
            else:
                htmls.append(buffer)
                buffer = ''
if buffer:
    htmls.append(buffer)
acc = 0
for i in htmls:
    acc += 1
    # print(i)
    # print('-\n'*20)
print('Number of chunks', acc)
print('Size first chunk:', len(htmls[0]))

# for i, html_chunk in enumerate(htmls):
#     # Create a BeautifulSoup object with the HTML chunk
#     soup = BeautifulSoup(html_chunk, 'html.parser')

#     # For each string in the BeautifulSoup object
#     for string in soup.strings:
#         # Define the data to send to the API
#         data = {
#             "q": string,
#             "source": "pt",
#             "target": "en",
#             "format": "text",
#         }

#         # Send a POST request to the API
#         response = requests.post(api_url, data=data)

#         if response.status_code == 200:
#             response_json = response.json()
#             if "translatedText" in response_json:
#                 translated_text = response_json["translatedText"]
#                 string.replace_with(translated_text)
#             else:
#                 print("Error: 'translatedText' key not found in response.")
#                 print("Response:", response_json)
#         else:
#             print("Error: API request failed.")
#             print("Status code:", response.status_code)
#             print("Response:", response.text)

#     # Update the HTML chunk with the translated HTML
#     htmls[i] = str(soup)

# Verifique se a pasta .out existe, se não, crie-a
if os.path.exists('.out'):
    shutil.rmtree('.out')
    os.makedirs('.out')

if not os.path.exists('.out'):
    os.makedirs('.out')

with open('.out/full_html_parsed.md', 'w', encoding='utf-8') as file:
    # Concatene todas as chunks e escreva o resultado no arquivo
    file.write(prompt + ''.join(htmls) + "\n```")
    #subprocess.run() with pretty-quick, in file, to format... how can I make this?

# Path to your Markdown file
# file_path = 'testazao/.out/full_html_parsed.md'


# # Run prettier to format the Markdown file
# subprocess.run(['pushd', 'D:/Projects'], check=True)
# subprocess.run(['prettier', '--write', file_path], check=True)

with open('.out/full_html_parsed.md', 'r', encoding='utf-8') as file:
    content = file.read()
pyperclip.copy(content)
print("Content copied!!")
for i, html_chunk in enumerate(htmls):
    with open(f'.out/html_chunk_{i}.md', 'w', encoding='utf-8') as file:
        file.write(prompt + html_chunk + "\n```")
# # Verifique se a pasta .out está vazia
# if not os.listdir('.out'):
# 	# Para cada elemento na lista htmls, crie um novo arquivo HTML na pasta .out
