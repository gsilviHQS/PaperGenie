#! /usr/bin/env python
import tkinter as tk
import os
# import sympy as sp
# from PIL import Image, ImageTk
# from io import BytesIO
# import textwrap

#MY FUNCTIONS
import functions
from Tkinter_helper import CustomText, custom_paste, HyperlinkManager,Interlink,COLOR_LIST, RightClicker


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.last_url = ''
        self.create_widgets()
                                   

    def create_widgets(self):
        # make a folder if it doesn't exist
        if not os.path.exists('papers'):
            os.makedirs('papers')
        
        
        # variables
        self.dollars = tk.DoubleVar()
        self.dollars.set(0.0)
        
        self.token_usage = tk.IntVar()
        self.token_usage.set(0)
        
        self.token_label = tk.StringVar()
        self.token_label.set('Usage: '+str(self.token_usage.get())+' tokens')
        
        self.papertitle = tk.StringVar()
        self.papertitle.set('\n')

        self.default_paper = tk.StringVar()
        
        self.default_paper.set("Papers")
        self.default_paper.trace("w", self.callback_to_url)

        # Column 0 widgets
        tk.Label(self.master, text="API Key").grid(row=0, column=0)
        self.apikey = tk.Entry(self.master, width=30)
        self.apikey.grid(row=1, column=0)
        self.apikey.bind('<Button-3>', RightClicker)

        tk.Label(self.master, text="arXiv URL").grid(row=2, column=0)
        self.url = tk.Entry(self.master, width=35)
        self.url.grid(row=3, column=0)
        self.url.bind('<Button-3>', RightClicker)
        # tk.Label(self.master, text="Paper title").grid(row=4, column=0)
        
        tk.Label(self.master, textvariable=self.papertitle, wraplength=500).grid(row=5, column=0)
        
        
        #option menu
        self.check_papers_in_folder() #check if there are papers in the folder
        if len(self.folders) > 0:
            self.folder_menu = tk.OptionMenu(self.master, self.default_paper, *self.folders)
            self.folder_menu.grid(row=3, column=0,sticky=tk.E)

        # section and subsection
        self.sections = CustomText(self.master, wrap=tk.WORD, width=70, height=50)
        self.sections.grid(row=6, column=0, rowspan=3)
        self.sections.bind('<Button-3>', RightClicker)
        
        
        #Column 1 widgets
        tk.Label(self.master, text="Question").grid(row=0,column=1, columnspan=2)
        self.question = tk.Text(self.master, wrap=tk.WORD, width=70, height=2)
        self.question.grid(row=1, column=1, columnspan=2)
        self.question.bind('<Button-3>', RightClicker)

        tk.Label(self.master, text="Keywords to search (separated by comma)").grid(row=2, column=1, columnspan=2)
        self.keybox = tk.Text(self.master, wrap=tk.WORD, width=70, height=2)
        self.keybox.grid(row=3, column=1, columnspan=2)
        self.keybox.bind('<Button-3>', RightClicker)
        tk.Label(self.master, text="Matching Phrases in tex files").grid(row=5, column=1, columnspan=2)
        tk.Label(self.master, text="Answer from GPT-3").grid(row=7, column=1, columnspan=2)

        #Column 2 widgets
        tk.Label(self.master, textvariable = self.token_label).grid(row=9, column=0 , sticky=tk.W)
        
        #Set defaults values
        # if api.txt exist then insert the content of api.txt into apikey entry else insert default value
        if os.path.isfile('API.csv'):
            with open('API.csv', 'r') as f:
                self.apikey.insert(0, f.read())
        else:
            self.apikey.insert(0, 'Your API Key here')
            # if apikey is selected by the user then cancel its content
            self.apikey.bind('<Button-1>', lambda event: self.apikey.delete(0, tk.END))
            tk.Button(self.master, text='Save API Key', command=self.save_api_key).grid(row=1, column=0, sticky=tk.W)

        # if default_values.csv exist then load url and question from default_values.csv
        if os.path.isfile('default_url.csv'):
            with open('default_url.csv', 'r') as f:
                self.url.insert(tk.END, f.read())
        if os.path.isfile('default_question.csv'):
            with open('default_question.csv', 'r') as f:
                self.question.insert(tk.END, f.read())
        #add one button to save default url
        tk.Button(self.master, text='Set default URL', command=self.save_url).grid(row=3, column=0, sticky=tk.W)
        #add one button to save default question
        tk.Button(self.master, text='Set default Question', command=self.save_question).grid(row=1, column=2, sticky=tk.E)


       
        self.question.focus()
        
         # new textbox for the phrases matching the question
        self.textbox2 = CustomText(self.master, height=20, width=90, wrap='word')
        self.textbox2.grid(row=6, column=1, columnspan=2)
        self.textbox2.bind('<Button-3>', RightClicker)
        self.textbox2.insert(tk.END, "Phrases")
        self.textbox2.config(state=tk.DISABLED,
                             background="white",
                             foreground="black",
                             font=("Helvetica", 11),
                             borderwidth=2,
                             )

        # output box to display the result
        self.textbox = tk.Text(self.master, height=20, width=90, wrap='word')
        self.textbox.grid(row=8, column=1, columnspan=2)
        self.textbox.bind('<Button-3>', RightClicker)
        self.textbox.insert(tk.END, "Output")
        self.textbox.config(state=tk.DISABLED,
                            background="white",
                            foreground="black",
                            font=("Helvetica", 11,'bold'),
                            borderwidth=2,
                            )
        
       


        #BUTTONS
        #button under url box named "Get paper"
        tk.Button(self.master, text='Get paper', command=self.get_paper).grid(row=4, column=0)

        tk.Button(self.master, text='Reset usage', command=self.reset_token_usage).grid(row=10, column=0, sticky=tk.W)                     

        tk.Button(self.master, text="Generate keywords from question", command=self.search_keywords).grid(row=4,
                                                                                          column=1, columnspan=2)

        self.boolean2 = tk.IntVar()
        self.boolean2.set(1)
        self.advance_prompt = tk.Checkbutton(self.master, text="Use advanced prompt", variable=self.boolean2).grid(row=9, 
                                                                                                     column=1, 
                                                                                                     sticky=tk.E)
        

        tk.Button(self.master, text='Run', command=self.run).grid(row=10,
                                                                  column=1,
                                                                  pady=4,
                                                                  sticky=tk.E)
        tk.Button(self.master, text='Quit', command=self.quit).grid(row=10,
                                                                    column=2,
                                                                    pady=4,
                                                                    sticky=tk.W)
        


    def callback_to_url(self,*args):
        self.url.delete(0, tk.END)
        url_to_use = "http://arxiv.org/abs/"+self.default_paper.get()
        self.url.insert(0,url_to_use)
        self.get_paper()

    def check_papers_in_folder(self):
        self.folders = list(os.listdir('papers/'))

    def reset_token_usage(self):
        self.token_usage.set(0)
        self.token_label.set('Usage: '+str(self.token_usage.get())+' tokens')
        self.dollars.set(0.0)

    def save_api_key(self):
        api_key = self.apikey.get()
        with open('API.csv', 'w') as f:
            f.write(api_key)
    
    def save_url(self):
        url = self.url.get()
        with open('default_url.csv', 'w') as f:
            f.write(url)
    
    def save_question(self):
        question = self.question.get("1.0", tk.END)
        with open('default_question.csv', 'w') as f:
            f.write(question)

    def update_token_usage(self,tokens, model):
        total_token_used = self.token_usage.get() #get the current token usage
        total_dollars_used = self.dollars.get() #get the current dollars usage
        
        total_token_used += tokens #add the tokens used to the total token usage
        self.token_usage.set(total_token_used) #update the token usage

        if model == 'text-davinci-002': #if the model is davinci
            dollars = tokens * (0.06/1000)
        elif model == 'text-curie-006': #if the model is curie
            dollars = tokens * (0.006/1000)
        elif model == 'text-babbage-001': #if the model is babbage
            dollars = tokens * (0.0012/1000)
        elif model =='text-ada-001': #if the model is ada
            dollars = tokens * (0.0008/1000)
        else:
            dollars = 0
        total_dollars_used += dollars #add the dollars used to the total dollars usage
        self.dollars.set(total_dollars_used) #update the dollars usage

        self.token_label.set('Usage: '+str(total_token_used)+' tokens ($'+"{:3.5f}".format(total_dollars_used)+')') #update the token usage label

    def get_paper(self):
        """ Get the paper from the url """
        url = self.url.get()  # get the url from the entry box
        tex_files,bibfiles = functions.getPaper(url)  # get the paper from arxiv
        print('tex_files found:', tex_files)
        self.complete_text = functions.extract_all_text(tex_files)  # extract the text from the paper
        self.bib_text = functions.extract_all_text(bibfiles)  # extract the text from the bib file
        print('bib_text found:', bibfiles)
        header = functions.getTitleOfthePaper(url) #get the title of the paper
        self.papertitle.set(header)  # set the papertitle label
        self.last_url = url  # save the last url
        #find section and subsection of the paper
        list_of_section = functions.get_sections(tex_files)
        list_of_section = functions.remove_duplicates(list_of_section, simplecase=True)
        print(list_of_section)
        self.sections.delete(1.0, tk.END)
        interlink = Interlink(self.sections, self.keybox, self.question)
        for i in list_of_section:
            self.sections.insert(tk.END, i)
            # apply the hyperlinks to the phrases
            self.sections.highlight_pattern(i,interlink)
        
        

    def search_keywords(self):
        api_key = self.apikey.get()
        question = self.question.get("1.0", tk.END)
        keywords, tokens, model = functions.promptText_keywords(question, api_key)
        self.update_token_usage(tokens, model)
        keywords = keywords.strip().strip('\n') #remove the newline character from the keywords
        # show keywords in the output box
        self.keybox.config(state=tk.NORMAL)
        # clear keybox
        self.keybox.delete(1.0, tk.END)  # clear the output box
        self.keybox.insert(tk.END, keywords)  # insert keywords in the keybox
        print('Keywords to use:', repr(keywords))
        return keywords

    def run(self):
        api_key = self.apikey.get()  # get the api key from the entry box
        question = self.question.get("1.0", tk.END)  # get the question from the entry box


        if self.last_url != self.url.get():  # if the url has changed
            self.get_paper()  # download the paper
        #TODO: apply the hyperlinks to the papertitle label, first change to a custom textbox
        
        #HANDLE THE KEYWORDS
        keywords = self.keybox.get("1.0", tk.END).strip()  # get the keywords from the output box        
        if keywords == '':  # if the keywords are not provided, promt GPT to generate them from the question
            keywords = self.search_keywords()
        print('Keywords in use:',keywords)

        # Get list_of_phrases from the text
        list_of_phrases = []
        number_of_phrases = 0
        
        for keyword in keywords.split(','):  # loop through the keywords
            phrase, stop, number_of_phrases = functions.extract_phrases(keyword.strip(), self.complete_text, api_key, number_of_phrases)
            
            if phrase is not None:
                list_of_phrases.extend(phrase)
                print('For keyword \'' + keyword + '\' the phrases found are:', len(phrase))
            else:
                print('For keyword \'' + keyword + '\' no phrase found')
                # # try lower case TODO: Improve lower/upper/plural/singular handling all in once
                    
            if stop:
                break  # if the stop flag is set, break the loop
      


        # Initialize the textbox to receive the generated text
        self.textbox.config(state=tk.NORMAL)
        self.textbox.delete(1.0, tk.END)

        if len(list_of_phrases) > 0: #if there are phrases!
            if self.boolean2.get() == 0:
                advance_search = False
            else:
                advance_search = True
            #print('list_of_phrases',list_of_phrases)
            # Here the code check if the user wants to use the check for relevance of each phrase,
            # otherwise it will just order phrases by most common according to keywords appearance
            # and limit the number to PHRASES_TO_USE (defined in functions.py)

            list_of_phrases = functions.connect_adjacent_phrases(list_of_phrases)  # connect adjacent phrases
            clean_list_of_phrases = functions.most_common_phrases(list_of_phrases,advance_search) # get the most common phrases
           

            just_phrases = []
            phrase_with_frequency = []
            for phrase in clean_list_of_phrases:
                just_phrases.append(phrase[0])
                phrase_with_frequency.append('('+str(phrase[1])+')'+phrase[0])

            #substitue in the phrases the \cite with the hyperlink to arxiv
            phrase_with_frequency, all_hyperlinks = functions.get_hyperlink(phrase_with_frequency, self.complete_text+self.bib_text)

            
            
            
            
            
            # MOST IMPORTANT STEP, ASK GPT-3 TO GIVE THE ANSWER
            try:
                if 'Summarize' in question or advance_search==False:
                    response = functions.promptText_question(question, just_phrases, self.papertitle.get(), api_key) #ask GPT-3 to give the answer
                    tokens = response['usage']['total_tokens']
                    model = response['model']
                    answer = response['choices'][0]['text']
                else:
                    response = functions.promptText_question2(question, just_phrases, self.papertitle.get(), api_key) #ask GPT-3 to give the answer
                    print(response)
                    tokens = 0
                    model = response['model'] #
                    answer= response['answers'][0]
                    phrase_to_sort= [(doc["score"],doc["text"]) for doc in response["selected_documents"]]
                    phrase_with_frequency = sorted(phrase_to_sort, key=lambda x: x[0], reverse=True)
                    #join the tuple in phrase_with_frequency
                    phrase_with_frequency = [str(x[0])+x[1] for x in phrase_with_frequency]
                self.update_token_usage(tokens, model) #update the token usage

                self.textbox.insert(tk.END, answer)  # insert the answer in the output box
                self.textbox.config(background="green") # change the background color of the output box
                self.textbox.after(400, lambda: self.textbox.config(background="white")) # reset the background color after 200ms
            except Exception as e:
                self.textbox.insert(tk.END, 'Error: ' + str(e))
                self.textbox.config(background="red") # change the background color of the output box
                self.textbox.after(400, lambda: self.textbox.config(background="white")) # reset the background color after 200ms
            

            # show the phrases in the output box
            self.textbox2.config(state=tk.NORMAL)
            self.textbox2.delete('1.0', tk.END)  # clear the output box
            self.textbox2.insert(tk.END, '-'+'\n-'.join(phrase_with_frequency))  # insert phrases in the textbox

            # apply the hyperlinks to the phrases
            hyperlink = HyperlinkManager(self.textbox2, self.url)
            for link in all_hyperlinks:
                self.textbox2.highlight_pattern(link,hyperlink)
  
            for k,keyword in enumerate(keywords.split(',')):
                #print(COLOR_LIST[k%len(COLOR_LIST)])
                self.textbox2.highlight_pattern(keyword, tag=COLOR_LIST[k%len(COLOR_LIST)])
            self.textbox2.config(state=tk.DISABLED)
        else:
            self.textbox.insert(tk.END, 'No phrases found in the paper matching the keywords. Try different keywords.')
        self.textbox.config(state=tk.DISABLED)




root = tk.Tk()
root.title("ArXiv Paper Genie: Q&A Tool with OpenAI GPT-3")
root.geometry("1500x800")
root.columnconfigure(3) 
root.configure(background="darkgray")
root.bind_class("Entry", "<<Paste>>", custom_paste)
root.grid_columnconfigure(0, weight=1) 
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
app = Application(master=root)
app.mainloop()
