# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

One bug I noticed was that the user could input guesses outside of the number range and also input negative numbers. It should throw a warning or error if the user tries to guess outside of the range. Another bug that I noticed was the number ranges for each of the difficulty levels was off. The normal level range was from 1-100, while the hard level range was smaller from 1-50, and I expected this to be flipped. Another bug that I noticed is the hints were backwards. For example, in one round the secret number was 75, so I guessed 76, but it hinted to "go higher". 


---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

I mostly used Copilot on this project, and ChatGPT for other questions (ex. remembering Git CLI commands). One example of an AI suggestion that was correct was handling out of bounds guesses in the parse_guess function in the logic_utils.py. The AI suggested adding min_val and max_val arguments to the function, and within the function it added a check to see if the guess was between the min_val and max_val bounds, otherwise throw a warning. I verified the result in my test case by testing values 1 below the min_val and 1 above the max_val. 

One AI suggestion that was incorrect was adjusting the number ranges for the "Normal" and "Hard" levels. I wanted to swap the original ranges such that Normal would be from 1-50 and Hard would be from 1-100. But after I made this fix, the AI assistant kept getting confused and trying to revert the change. In the end, I just ignored that specific suggested edit from Copilot. 

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

For example, to test the inputs out of the range, I create a simple pytest. I also tried a few manual values, especially extreme positive and negative values (ex. -10000000, 10000000, etc.). However when trying these guesses, something I realized about my code was that I was unsure how it was handling decimals (ex. 40.3). I then asked Copilot to explain how this functionality was being handled, and suggestions to handle non-integer inputs. 

Using AI streamlined the manual process of creating small unit tests. Sometimes, I would also experiment with manual tests, discover new bugs, and use the AI to understand intended functionality and debug. 

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

The secret number kept changing in the original app because Streamlit reruns the script after every guess. So even within the same round, even if I submit an initial guess, the number would change right after that. Streamlit reruns the entire Python app.py file every single time you open it and during every interaction during that session when you have the browser tab open. Thats why you need to store static data in the session state which stays the same during a single session. To give the app a stable secret number, I generated it randomly and I stored it in st.session_state. 


---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

One strategy from this project I want to reuse is definitely being comfortable using AI to help ideate and iterate new features and physically develop them out. But I also want to be critical about the way I use AI and make sure that I'm always validating and fully understanding the suggested changes before accepting them. Next time I work with AI on a coding task, I think the first prompt I will ask it is to walk me through the entire codebase, just to get familiar with the functions and files before having Copilot go through the code and suggest changes. This will also help me understand how the code is organized and if later down the line, I'm going to have to do any reorganization or consolidation of code logic. One way this project changed the way I think about AI generated code is that sometimes, you have to be careful about the output because it can be unnecessarily complex and not exactly what you intended. For example, I had to use very specific language to get it to build out the guess history feature how I wanted. 