# This is a sample Python script.
import openai

from algorithm.OpenAI.scraper import Scraper

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#
openai.api_key = "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"

def ask(dict, prompt):
    # create a chat completion
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": str(dict)+" "+prompt}])
    # print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


# Press the green button in the gutter to run the script.
def get_details_from_openai(url):
    scrap = Scraper()
    prompt = "create a 60 seconds Pitch sale in form of text"
    scrap.scrape(url)
    # print(scrap.infoDict)
    resp = ask(str(scrap.infoDict), prompt)
    return resp


# See PyCharm help at https://www.jetbrains.com/help/pycharm/