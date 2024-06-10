from colorama import Fore, Style

import openai

import subprocess
import re

# insert OpenAI org and secret API key here:
OPENAI_ORG = ""
OPENAI_KEY = ""

# printMessage takes in a message dict and formats it to print
def printMessage(message: dict, commandFlag: bool = False):
    match message["role"]:
        case "system":
            brightness=Style.BRIGHT
            colour=Fore.MAGENTA
        case "user":
            if commandFlag:
                brightness=Style.NORMAL
                colour=Fore.GREEN
            else:
                brightness=Style.NORMAL
                colour=Fore.BLUE
        case "assistant":
            brightness=Style.NORMAL
            colour=Fore.LIGHTRED_EX
        case _:
            brightness=Style.NORMAL
            colour=Fore.BLACK
    print(f"{brightness}{colour}<{message['role']}>: {message['content']}{Style.RESET_ALL}")

if __name__ == "__main__":
    
    print("Starting LT's bash LM scaffold...\n")

    # initialise the OpenAI client
    client = openai.OpenAI(organization=OPENAI_ORG, api_key=OPENAI_KEY)

    # initialise a messages list that will store all the messages in the conversation
    messageStore = []

    # initialise the system message to be used for all conversations
    systemMessage = {"role": "system", "content": "You are being run in a scaffold in a shell on a Linux virtual machine. When you want to run a shell command, write it in a <bash> XML tag. You will be shown the result of the command and be able to run more commands. Other things you say will be sent to the user. In cases where you know how to do something, don't explain how to do it, just start doing it by emitting bash commands one at a time. You are in a bash shell. Remember that you can't interact with stdin directly, so if you want to e.g. do things over ssh you need to run commands that will finish and return control to you rather than blocking on stdin. Don't wait for the user to say okay before suggesting a bash command to run. If possible, don't include explanation, just say the command.\n\nIf you can't do something without assistance, please suggest a way of doing it without assistance anyway."}

    # initialise necessary flags
    newConversation = True
    commandGiven = False
    commandFlag = False

    # set up a loop that will repeat until the break command is given:
    while True:

        # if new conversation, print system message and add to messageStore
        if newConversation:
            printMessage(systemMessage)
            messageStore.append(systemMessage)
            newConversation = False

        # get the most recent message in the conversation
        lastMessage = messageStore[-1]

        # if last message is from assistant, check for <bash> XML tag
        if lastMessage["role"]=="assistant" or lastMessage["content"]=="<bash>dir</bash>":
            m = re.findall(r"<bash>(.*)<\/bash>", lastMessage["content"])
            # if the assistant suggests a command, store it and suggest it for the user
            if m != []:
                command = m[0]
                print(f"(enter to run `{command}`)", end="")
                commandGiven = True
            else:
                command = ""
                commandGiven = False
        
        # then ask user for input
        userInput = input("> ")
        
        # if no input given, just reprompt
        if not commandGiven and userInput == "":
            continue

        # if specifically '<new>' is given, restart conversation
        elif userInput == "<new>":
            messageStore = []
            newConversation = True
            commandGiven = False
            commandFlag = False
            continue

        # if specifically '<exit>' is given, quit
        elif userInput == "<exit>":
            break
        
        # if there is a command queued and user has pressed enter, run command
        elif commandGiven and userInput=="":
            output = subprocess.run(command.split(), capture_output=True, text=True, timeout=10, shell=True)
            if output.stdout == "":
                nextMessage = {"role": "user", "content": output.stderr}
            else:
                nextMessage = {"role": "user", "content": output.stdout}
            commandGiven = False
            commandFlag = True
        
        # otherwise, add user input as next message (unless blank, in which case, skip)
        elif userInput!="":
            nextMessage = {"role": "user", "content": userInput}
            commandGiven = False
            commandFlag = False

        # add the next message to the messageStore
        messageStore.append(nextMessage)
        printMessage(nextMessage, commandFlag)

        # now make a request to GPT-4 to continue the message history
        stream = client.chat.completions.create(
            model="gpt-4",
            messages=messageStore,
            stream=True
        )

        fullContent = []
        print(f"{Style.NORMAL}{Fore.RED}<assistant>: {Style.RESET_ALL}", end="", flush=True)
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                fullContent.append(chunk.choices[0].delta.content)
                print(f"{Style.NORMAL}{Fore.RED}{chunk.choices[0].delta.content}{Style.RESET_ALL}", end="", flush=True)
        
        print()
        modelResponse = {"role": "assistant", "content": "".join(fullContent)}
        messageStore.append(modelResponse)
