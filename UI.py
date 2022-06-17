import tkinter as tk 

import functions
import os

default_url = 'https://arxiv.org/abs/2101.08448'
default_question = 'Summarize the abstract'


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="API Key").grid(row=0)
        tk.Label(self.master, text="arXiv URL").grid(row=1)
        tk.Label(self.master, text="Question").grid(row=2)
        tk.Label(self.master, text="Keywords to search").grid(row=3)
        tk.Label(self.master, text="Paper").grid(row=4)
        tk.Label(self.master, text="Answer").grid(row=5)

        self.papertitle = tk.StringVar()
        self.papertitle.set('\n')
        tk.Label(self.master, textvariable=self.papertitle, wraplength=500).grid(row=4, column=1)

        self.apikey = tk.Entry(self.master, width=30)

        # if api.txt exist then insert the content of api.txt into apikey entry else insert default value
        if os.path.isfile('API.txt'):
            with open('API.txt', 'r') as f:
                self.apikey.insert(0, f.read())
        else:
            self.apikey.insert(0, 'Your API Key here')
        
        self.url = tk.Entry(self.master, width=50)
        self.url.insert(0, default_url)
        self.question = tk.Entry(self.master, width=50)
        self.question.insert(0, default_question)

        self.apikey.grid(row=0, column=1)
        self.url.grid(row=1, column=1)
        self.question.grid(row=2, column=1)

        self.keybox = tk.Text(self.master, width=50, height=1)
        self.keybox.grid(row=3, column=1)
        # self.keybox.config(state=tk.DISABLED)

        # output box to display the result
        self.textbox = tk.Text(self.master, height=40, width=90)
        self.textbox.grid(row=5, column=1, columnspan=2)
        self.textbox.insert(tk.END, "Output")
        self.textbox.config()
        self.textbox.config(state=tk.DISABLED,
                            background="white",
                            foreground="black",
                            font=("Helvetica", 11),
                            borderwidth=2,
                            )

        tk.Button(self.master, text="Search keywords", command=self.search_keywords).grid(row=3,
                                                                                          column=2,
                                                                                          sticky=tk.W)
        #add boolean variable 
        self.boolean = tk.IntVar()
        self.boolean.set(0)
        #add checkbox below search keywords button to ask for synonims
        self.checkbox = tk.Checkbutton(self.master, text="and synonyms", variable=self.boolean).grid(row=4, 
                                                                                                     column=2, 
                                                                                                     sticky=tk.W)
        

        tk.Button(self.master, text='Run', command=self.run).grid(row=6,
                                                                  column=1,
                                                                  pady=4)
        tk.Button(self.master, text='Quit', command=self.quit).grid(row=7,
                                                                    column=1,
                                                                    pady=4)

    def search_keywords(self):
        api_key = self.apikey.get()
        question = self.question.get()
        # print value of boolean variable
        if self.boolean.get() == 1:
            keywords = functions.promptText_keywords(question, api_key, True).strip('\n')
        else:
            keywords = functions.promptText_keywords(question, api_key).strip('\n')
        # show keywords in the output box
        self.keybox.config(state=tk.NORMAL)
        self.keybox.delete('1.0', tk.END)  # clear the output box
        self.keybox.insert(tk.END, keywords)  # insert keywords in the keybox
        return keywords

    def run(self):
        api_key = self.apikey.get()  # get the api key from the entry box
        question = self.question.get()  # get the question from the entry box
        url = self.url.get()  # get the url from the entry box

        tex_files = functions.getPaper(url)  # get the paper from arxiv
        print('tex_files:', tex_files)
        self.papertitle.set(functions.getTitleOfthePaper(url))  # set the title of the paper label from the url

        keywords = self.keybox.get("1.0", tk.END).strip()  # get the keywords from the output box in lower case        
        if keywords == '':  # if the keywords are not provided, promt GPT to generate them from the question
            keywords = self.search_keywords()

        print('Keywords to use:', keywords)
        # get list_of_phrases from the text
        list_of_phrases = []
        complete_text = functions.extract_all_text(tex_files)
        for keyword in keywords.split(','):  # loop through the keywords
            phrase, stop = functions.extract_phrases(keyword.strip(), complete_text, api_key)
            if stop:
                break
            if phrase is not None:
                list_of_phrases.append(".\n".join(phrase))
                print('For keyword \'' + keyword + '\' the phrase found are:', phrase)
            else:
                phrase_lower = functions.extract_phrases(keyword.strip().lower(), complete_text, api_key)  # try lower case
                if phrase_lower is not None:
                    list_of_phrases.append(".\n".join(phrase_lower))
                    print('For keyword \'' + keyword.strip().lower() + '\' the phrase found are:', phrase_lower)
                else:
                    print('For keyword \'' + keyword + '\' no phrase found')
        list_of_phrases = ".\n".join(list_of_phrases)

        # print('Phrases (',len(list_of_phrases),')',list_of_phrases)
        self.textbox.config(state=tk.NORMAL)
        self.textbox.delete(1.0, tk.END)
        if len(list_of_phrases) > 0:
            header = functions.getTitleOfthePaper(url)
            try:
                result = functions.promptText_question(question, list_of_phrases, header, api_key)
                self.textbox.insert(tk.END, result['choices'][0]['text'])  # insert the answer in the output box
            except Exception as e:
                self.textbox.insert(tk.END, 'Error: ' + str(e))
            
        else:
            self.textbox.insert(tk.END, 'No phrases found in the paper matching the keywords. Try different keywords')
        self.textbox.config(state=tk.DISABLED)


root = tk.Tk()
root.title("ArXiv Question Answering with GPT-3 OpenAI")
root.geometry("1000x800")
root.columnconfigure(3)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
app = Application(master=root)
app.mainloop()