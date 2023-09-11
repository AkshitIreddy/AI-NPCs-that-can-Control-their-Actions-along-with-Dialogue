from langchain.llms import Cohere
from langchain import PromptTemplate, LLMChain
from functions.generate_music_function import generate_music
import assemblyai as aai
from dotenv import load_dotenv
import speech_recognition as sr
import requests
import shutil
import time
import json
import re
import os

load_dotenv(dotenv_path='.env')

character_name_file_path = r"Project\Content\text_files\character_identification.txt"
start_python_file_path = r"Project\Content\text_files\start_python.txt"
python_completed_file_path = r"Project\Content\text_files\python_completed_flag.txt"
output_audio_destination_path = r"Project\Content\audio\output.mp3"
output_music_destination_path = r"Project\Content\audio\music.mp3"
action_path = r"Project\Content\text_files\action.txt"

# Load data from the JSON file
with open('character_info.json', 'r') as json_file:
    character_info = json.load(json_file)

while True:

    # Check start python text file
    with open(start_python_file_path, 'r') as file:
        start = file.read()

    #if it is 0 then sleep and continue 
    if start == '0':
        time.sleep(1)
        continue

    # Set the start file back to 0
    with open(start_python_file_path, 'w') as file:
        file.write('0')

    # Capture audio from microphone
    # Initialize the Recognizer

    r = sr.Recognizer()

    # Obtain audio from the microphone
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    # Save the audio to a file named 'test.wav'
    with open("input.wav", "wb") as audio_file:
        audio_file.write(audio.get_wav_data())

    print("Audio saved as input.wav")

    # Speech Recognition using Assembly AI
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe("./input.wav")

    player_dialogue = transcript.text
    print(player_dialogue)

    # find out who the player is speaking to
    with open(character_name_file_path, 'r') as file:
        character_name = file.read()

    bio = character_info[character_name]['bio']

    # Check if character_name exists in character_info
    if character_name in character_info:
        character_data = character_info[character_name]
        
        # Create a string for actions
        actions_string = "\n".join([f"{action}: {description}" for action, description in character_data["actions"].items()])
        
        # Create a string for talking style
        talking_style_string = "\n".join(character_data["talking_style"])

    # Load data from conversation.json
    with open('conversation.json', 'r') as json_file:
        data = json.load(json_file)

    # Extract dialogues and actions and concatenate into a paragraph
    conversation_string = ''
    for entry in data['conversations']:
        conversation_string += f"{entry['character']}: {entry['dialogue']}\n(Action: {entry['action']})\n"

    # embeddings = CohereEmbeddings(cohere_api_key=os.getenv("COHERE_API_KEY"))
    # persist_directory = 'vectordb'
    # vectordb = Chroma(persist_directory=persist_directory,
    #                     embedding_function=embeddings)
    # docs = vectordb.similarity_search(conversation_string, k=3)
    # memory_string = "\n".join(doc.page_content for doc in docs)

    # Initialise model
    llm = Cohere(cohere_api_key=os.getenv("COHERE_API_KEY"),
                    model='command', temperature=0, max_tokens=300, stop=['Hadley Smith:', "Ettore Johnson:", "Player:"])

    # Create the template string
    template = """Bio of {character_name}: \n{bio}\n\nTalking Style of {character_name}: \n{talking_style_string}\n\nActions {character_name} can do:\n{actions_string}\n\nThis is a conversation between NPCs and a Player. The NPCs must give very very small responses followed by action at all costs. The NPCs must give responses according to their talking style and must give out a "Action"(Only give action name not description) at the end of their response.\n{conversation_string}Player: {player_dialogue}\n(Action: Idle)\n{character_name}:"""

    # Create prompt
    prompt = PromptTemplate(template=template, input_variables=['conversation_string', 'bio', 'character_name', 'talking_style_string', 'player_dialogue', 'actions_string'])

    # Create and run the llm chain
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    response = llm_chain.run(conversation_string=conversation_string, bio=bio, character_name=character_name, talking_style_string=talking_style_string, player_dialogue=player_dialogue, actions_string=actions_string)

    print(prompt.format_prompt(conversation_string=conversation_string, bio=bio, character_name=character_name, talking_style_string=talking_style_string, player_dialogue=player_dialogue, actions_string=actions_string).text)
    print(response)
    
    # Define a regular expression pattern to match the Action
    action_pattern = r'\(Action: (.+?)\)'

    # Use the re.search() function to find the action
    action_match = re.search(action_pattern, response)

    if action_match:
        action = action_match.group(1)
    
    response = response.replace(action_match.group(0), '').strip()

    print("Extracted Action: " + action)
    print("Extracted Response: " + response)

    # Create a new conversation entry for the player dialogue
    player_dialogue_entry = {
        "character": "Player",  
        "dialogue": player_dialogue, 
        "action": "Idle"  
    }

    # Create a new conversation entry for the response
    response_entry = {
        "character": character_name,  # The character responding
        "dialogue": response, # The response generated by the LLM
        "action": action  # The action suggested by the LLM
    }

    # Append the player's dialogue to the conversation
    data["conversations"].append(player_dialogue_entry)

    # Append the response entry to the conversation
    data["conversations"].append(response_entry)

    # Save the updated JSON data back to the file
    with open('conversation.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)


    # Create Voice using Elevenlabs
    CHUNK_SIZE = 1024
    id = ""
    if character_name == "Hadley Smith":
        id = "21m00Tcm4TlvDq8ikWAM"
    elif character_name == "Ettore Johnson":
        id = "ODq5zmih8GrVes37Dizd"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{id}"

    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": os.getenv("ELEVENLABS_API_KEY")
    }

    data = {
    "text": response,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    # Copy the generated audio to the unreal engine project
    shutil.copy('output.mp3', output_audio_destination_path)
    
    # write the action to be performed
    with open(action_path, 'w') as file:
        file.write(action)
    
    if action == "Musica Harmoniosa Creatus":
        generate_music()
        # Copy the generated music to the unreal engine project
        shutil.copy('musicgen_out.mp3', output_music_destination_path)
    
    # set the complete flag to 1
    with open(python_completed_file_path, 'w') as file:
        file.write('1')