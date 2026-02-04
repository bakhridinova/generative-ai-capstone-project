# [Capstone project 1 - Chat with data](https://github.com/bakhridinova/generative-ai-capstone-project/tree/master/chat_with_data)

**DATA INSIGHTS APP**

Agent should assist user in getting information from the database. Datasource should not go to LLM fully (in prompt), only part of it may pass through, e.g. extracted chunks or output from the DB.

User interface should reflect some business information apart of chat. As an example, some aggregated information about the datasource (rows count etc.), or chart/table/contact info/sample queries.

Agent should print logs to the console.

Agent should offer user to create a support ticket to reach the human. This may be triggered explicitly, by asking the agent, as well as the agent may suggest it when necessary. Support ticket may be in any issue tracking system, like github, trello or jira.

Function call usage is a must.

**Non-functional requirements**

Code should be in root branch (main/master)

Data should have at least 500 rows or entities

Agent should be build with python

UI should be build with Streamlit

At least 2 tools different should be used in function calling

Instruction is required in README with screenshots from real usage example, showing the workflow from start to finish

Agent should be configured with safety feature stopping it from dangerous operations like deleting items or tables

Bonus points for hosted solution like HF Spaces


# [Capstone project 2 - voice to image](https://github.com/bakhridinova/generative-ai-capstone-project/tree/master/voice_to_image)

**VOICE TO IMAGE APP**

Agent should take a short voice message as an input

LLM should convert user request to image description for image generation model

Image model generates the picture and gives it back to the user

User interface should reflect all the intermediate data, like recorded message transcript, prompt for image generator, models used etc.

Agent should print logs to the console.


**Non-functional requirements**

Code should be in root branch (main/master)

Agent should be build with python

UI should be build with Streamlit

Instruction is required in README with screenshots from real usage example, with workflow from start to finish

Bonus points for hosted solution like HF Spaces