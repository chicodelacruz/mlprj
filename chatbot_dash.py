import os
import time
from textwrap import dedent

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from PIL import Image
import openai
#import configuration

def create_jsonlfile():

    #Paste the API KEY
    openai.api_key ="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"   

    #Create the documents file as jsonl file
    document_path = "jsonlfiles/gpt3.jsonl"
    file = openai.File.create(file=open(document_path), purpose='answers')
    return file

def generateAnswers(user_question, jsonl_file, temp=0.6, maxtoken=50):
   
   try:
    response =openai.Answer.create(
        search_model="ada", 
        model="curie", 
        question=user_question,       
        
        file=jsonl_file["id"], 
        examples_context="I was asked to write twenty yes or no questions about this text of questions", 
        examples=[["Is he the most versatile actors of his day?", "Yes"],
                  ["Is he a painter?", "No"],
                  ["Is he a theater actor?", "Maybe"],
                  ["Is he a movie actor?", "Yes"],
                  ["What is the color of the eyes?", "Question should be answerable by yes or no"]
                  ],
        max_rerank=10,
        max_tokens=maxtoken,
        temperature=temp,
        stop=["\n"]
    )

    return response
   
   except :
       response ={"answers": [" Not related, please ask again. "] }
       return response

print("Creating file !")
file =create_jsonlfile() 
print("File created!! File id: ",file["id"])   


def Header(name, app):
    title = html.H1(name, style={"margin-top": 10})
    # logo = html.Img(
    #     src=app.get_asset_url("logo.jpeg"), style={"float": "left", "height": 100}
    # )
    return dbc.Row([dbc.Col(title, md=8)])


def textbox(text, box="AI", name="Chico"):
    text = text.replace(f"{name}:", "").replace("You:", "")
    style = {
        "max-width": "60%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = 0
        style["margin-right"] = 0

        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = 0

        # thumbnail = html.Img(
        #     src=app.get_asset_url("Philippe.jpg"),
        #     style={
        #         "border-radius": 50,
        #         "height": 36,
        #         "margin-right": 5,
        #         "float": "left",
        #     },
        # )
        textbox = dbc.Card(text, style=style, body=True, color="light", inverse=False)

        return html.Div([textbox])

    else:
        raise ValueError("Incorrect option for `box`.")


description = """
Chico is a Fullstack Developer.
"""

# Authentication
#openai.api_key = os.getenv("OPENAI_KEY")

# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


# Load images
#IMAGES = {"Philippe": app.get_asset_url("Philippe.jpg")}


# Define Layout
conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(90vh - 132px)",
        "flex-direction": "column-reverse",
    },
)

controls = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="ask...", type="text"),
        dbc.InputGroupAddon(dbc.Button("Submit", id="submit"), addon_type="append"),
    ]
)

app.layout = dbc.Container(
    fluid=False,
    children=[
        Header("Category for today: Male Actor", app),
        html.Hr(),
        dcc.Store(id="store-conversation", data=""),
        conversation,
        controls,
        dbc.Spinner(html.Div(id="loading-component")),
    ],
)


@app.callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]


@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""


@app.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data")],
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None

    name = "Chico"

    prompt = dedent(
        f"""
    {description}
    You: Hello {name}!
    {name}: Hello! Glad to be talking to you today.
    """
    )

    # First add the user input to the chat history
    chat_history += f"You: {user_input}<split>{name}:"

    model_input = prompt + chat_history.replace("<split>", "\n")

   

    #user_ques =input("Chatbot - Enter your question :")
    response = generateAnswers(user_input, file)
    #full_answer = check_scores(model_input, response)
    # # print("Chatbot Answer :", response["answers"][0])
    # print("Chatbot Answer :", full_answer.answer)
    # if full_answer.additional:
    #     print("Additionally:\n")
    #     print(full_answer.additional)

    # response = openai.Completion.create(
    #     engine="davinci",
    #     prompt=model_input,
    #     max_tokens=250,
    #     stop=["You:"],
    #     temperature=0.9,
    # )
    #model_output = response.choices[0].text.strip()
    model_output=response["answers"][0]
    chat_history += f"{model_output}<split>"

    return chat_history, None


if __name__ == "__main__":
    app.run_server(debug=False)