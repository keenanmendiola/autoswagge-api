from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import streamlit as st
from dotenv import load_dotenv
import os
from langchain import OpenAI, PromptTemplate, HuggingFaceHub
from langchain.agents import AgentType
from langchain.agents.agent_toolkits import create_python_agent
from langchain.tools.python.tool import PythonREPLTool
from langchain.python import PythonREPL
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
import openai
import json
import ast
import re
import requests
import pandas as pd

app = Flask(__name__)
CORS(app)

openai.api_key=os.getenv('OPEN_API_KEY')

@app.route('/swagger', methods=['POST'])
def readSwaggerDoc():
    data = request.json
    output = readSwaggerDoc(data["swaggerUrl"])
    url = find_url(output)
    response = {'data': url}
    return make_response(jsonify(response), 200)


@app.route('/generate-code', methods=['POST'])
def generateCode():
    data = request.json
    url = data["url"]
    verb = data["verb"]
    generatedCode = generateCodeForPath(url, verb)
    response = {'data': generatedCode}
    return make_response(jsonify(response), 200)

@app.route('/get-base-url', methods=['POST'])
def getBaseUrl():
    data = request.json
    swaggerJson = data["swaggerJson"]
    url = find_url(json.dumps(swaggerJson))
    baseUrl = getBaseApiURL(url)
    response = {'baseUrl': baseUrl}
    return make_response(jsonify(response), 200)

def find_url(string):
    regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    url = re.search(regex, string)
    
    if url:
        return url.group()
    else:
        return None
    
def getBaseApiURL(url):
    template = """
            ### System:
            Understand, you are a senior back end developer specialising in API integration.
            A swagger documentation provides endpoint details such as request body, parameters, queries.

            ### User:
            Analyze the API document in the Swagger URL and answer with the following:
            - The base url for the API, only answer with the base url.

            ### URL:
            {url}
        """
    
    prompt = PromptTemplate(
        input_variables=["url"],
        template = template
    )

    final_prompt = prompt.format(url=url)

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=final_prompt,
        max_tokens=2048, 
        n=1,            
        stop=None,       
        temperature=0  
    )
    request =  response.choices[0].text.strip()
    
    return request 

def generateCodeForPath(url, verb):
    template = """
            ### System:
            You are a senior back end developer specialising in API integration.
            
            ### User:
            Create a python function to perform a network request based on the provided url and http verb below.
            Show in the code the variable initialization and assignments.
            Show also in the code the function call.
            Include any necessary imports in your code
            Your answer should only be the python code.

            ### url:
            {url}
            ### http verb:
            {verb}
        """
    
    prompt = PromptTemplate(
        input_variables=["url", "verb"],
        template = template
    )

    final_prompt = prompt.format(url=url, verb=verb)


    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=final_prompt,
        max_tokens=2048, 
        n=1,            
        stop=None,       
        temperature=0  
    )
    code =  response.choices[0].text.strip()
    return code

def readSwaggerDoc(swaggerLink):
    template = """
        ### System:
        Understand, you are a senior back end developer specialising in API integration.
        A swagger documentation provides a list of endpoints and its details such as request body, parameters, queries.

        ### User:
        Analyze the API document in the Swagger URL and answer with the following:
            - the link to the JSON file of the Swagger URL, only return the link of the JSON file.
        It is possible that the JSON file link is written in a different format.
        
        ### URL:
        {URL}
    """
    
    prompt = PromptTemplate(
        input_variables=["URL"],
        template = template
    )

    final_prompt = prompt.format(URL=swaggerLink)

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=final_prompt,
        max_tokens=2048, 
        n=1,            
        stop=None,       
        temperature=0  
    )
    swaggerJsonLink =  response.choices[0].text.strip()
    
    return swaggerJsonLink 

def find_url(string):
    regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    url = re.search(regex, string)
    
    if url:
        return url.group()
    else:
        return None

if __name__ == '__main__':
    app.run()
