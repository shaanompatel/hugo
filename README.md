# Foreman
Foreman, powered by Hugo, makes managing supplies simple: ask anything about inventory and suppliers, let Hugo handle vendor emails, find the best suppliers, and get clear stock forecasts.
## Inspiration
Every hardware startup experiences hardship in managing and optimizing the supply chain with multiple suppliers as there are numerous different factors to be considered. With Dryft providing us data about a specific hardware company to create Hugo, an AI assistant for industrial procurement, motivated us to resolve this issue. 

## What it does
The website Foreman provides three main features utilizing Hugo:
1. Chatbot Insight - Hugo provides insights on inventory, vendors, and procurement data upon queries. 
2. Smart Inbox - Hugo responds to the emails that are from the vendors and note the change in the company database or try and negotiate a deal if there is a change in price which affects the supply chain negatively.
3. Supply Chain Graph - A real-time graph visualization which finds the cheapest suppliers to order the supplies from. This update gets triggered when a change is made to a database.

## How we built it
We have used Python, specifically Django, to provide the server for the web service. Gemini 2.5 API has been prompted for the responses of the LLM based on the current database. SQLite is used to store the data efficiently for the LLM to utilize and modify. 

## Challenges we ran into
One of the largest challenge was to make Hugo reliably query the database and make suitable changes if needed. As we have enabled Hugo to directly modify the database, we had to be very careful on how Hugo processes the given data. Preventing it to query irrelevant data and referencing in its response to an email or a question was another challenge. 

## Accomplishments that we're proud of
Being able to make Hugo automatically respond to the vendors and even negotiating the prices if needed is something that we are proud of. Hugo supports its argument with data from the SQL database by querying relevant data and providing reasons why it would be discouraging for increasing the price. 

## What's next for Foreman
We would like to even more optimize the future ordering plans for Voltway. Being able to reliably have minimal number of stocks yet not wasting them by over ordering remains a large pain point in the hardware industry. We would like to further tackle this issue in the future with Foreman.