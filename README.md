# LMBash
Simple Python scaffold for conversing with GPT-4 while allowing it to execute bash commands under supervision.

This scaffold has the following features:
- enables user-assistant conversation (as expected for ChatGPT);
- GPT-4 responses printed to terminal via stream (so as and when you get the tokens);
- different colours corresponding to different conversation roles; and
- detects when GPT-4 response contains `<bash>...</bash>` and allows quick execution of shell command by pressing enter.

No LMs were used to write this code.
This took probably just over 2 hours of solid work (broken up through the day).
Major points of work include:
- setting up OpenAI account, API key, and credit;
- familiarising with subprocess and colorama modules; and
- setting up loop to facilitate ongoing conversation.
