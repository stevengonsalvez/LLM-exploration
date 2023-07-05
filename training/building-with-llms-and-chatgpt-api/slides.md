---
theme: academic
class: text-white
colorSchema: dark
coverBackgroundUrl: https://images.unsplash.com/photo-1607799279861-4dd421887fb3
coverBackgroundSource: unsplash
coverBackgroundSourceUrl: https://unsplash.com/photos/8qEB0fTe9Vw
coverDate: 12/01/2022
exportFilename: Engineering with LLMs
fonts:
  local: Monserrat, Roboto Mono
hideInToc: true
info: |
  Engineer with LLMS
lineNumbers: true
titleTemplate: '%s • Digital Engineering'
---

# Engineer with LLMs - Part 1

Not another Brown bag

<div class="pt-12">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
    Press Space for next page <carbon:arrow-right class="inline"/>
  </span>
</div>

<div class="abs-br m-6 flex gap-2">
  <button @click="$slidev.nav.openInEditor()" title="Open in Editor" class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon:edit />
  </button>
  <a href="https://github.com/stevengonsalvez/LLM-dojo" target="_blank" alt="GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

<!--

-->

---
layout: image
image: https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=987&q=80
---

# Agenda

<div class="font-mono grid grid-cols-4 gap-3 text-sm">
  <div class="bg-green-500/50 px-3 py-2 rounded w-full" v-click>
    <h4>Part 1</h4>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">How LLMs work, models, format, tokens</div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"><p class="text-center">Classification, moderation</p></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"><p class="text-center">Chain of thought, prompting chains</p></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"><p class="text-center">Output Validations</p></div>
  </div>
  <div class="bg-gray-500/50 px-3 py-2 rounded w-full" v-click>
    <h4>Part 2</h4>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">Prompt Engineering deepdive</div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">Evaluation and Testing</div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">Prompt techniques explore</div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">N-shot, retrieval-augmentation, Generated knowledge prompt, tree-of-thought </div>  
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">ethical prompt hacking</div>  
  </div>
  <div class="bg-gray-500/50 px-3 py-2 rounded w-full" v-click>
    <h4>Part 3</h4>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">Langchain framework exploration</div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">Autonomous AGIs, AutoGPT, gpt-engineer, smol</div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">Different models, LLAMA, PALM2, Anthropic</div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">Platforms for AI apps</div>
  </div>
  <div class="bg-gray-500/50 px-3 py-2 rounded w-full" v-click>
    <h4>Part 4</h4>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">How Diffusion models work</div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full">Training models with your data</div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
  </div>
</div>

---

# How does LLM work - 1

> You are probably familiar with the text generation process, likely completions given a prompt

<br/>

>prompt
<p class="text-2xl"  style="color:green">"I love eating"</p>
<div v-click class="text-sm p-2">

- pizza, especially with extra cheese and toppings
- fresh fruits, they are so delicious and healthy
- homemade chocolate chip cookies straight from the oven
</div>

<!--Notes: 
How did the model learn to do this -> next slide
-->
---

# How does LLM work - 2

> <span style="background-color:green">what is?</span>   
> Supervised Learning ( A -> B). A computer learns an input -> output mapping using labelled data.

<br/>

<div v-click>

<p class="text-sm"  style="color:green"> > example of labelled data for building a model to classify sentiments</p>

| Input                    | output   |
| ------------------------ | -------- |
| The pancake was delicious  | positive |
| The service was poor     | negative |
| The ambience was awesome | positive |

</div>

<!--Notes: 
- The main tools to train LLM is supervised learning
- In supervised learning, a computer learns an input-output mapping using some labelled data 
- (e.g: as on screen) if we are using some data to classify restaurant reviews 
-->


---

# How does LLM work - 3


> LLMs are built using supervised learning to repeatedly predict the next word. 

<span style="background-color:grey">e.g: taking some labelled training data</span> <p class="text-sm"  style="color:green">"My favorite hobby is playing the guitar and creating music"</p>
<div v-click class="text-sm p-4">

| Input                                       | output         |
| ------------------------------------------- | -------------- |
| My favorite                                 | hobby is       |
| My favorite hobby is                        | playing        |
| My favorite hobby is playing the            | guitar         |
| My favorite hobby is playing the guitar and | creating music | 
</div>

<!--Notes: 
- This sentence is turned into a sequence of training examples, where given sentence fragments - it predicts the next word from the sentence fragments
- given the large training set of 100s of billions, a massive training set is created to train the model to learn to predict what the next word/fragment is
-->

---

# Types of LLMS

> - Base LLM
> - Instruction tuned LLMs

<div v-click>

- <span style="background-color:green">Base LLM</span>
  - Repeatedly predicts next word based on training data

>e.g. Once there was a Goat named Oliver<p class="text-xs"  style="color:green">whose mischievous antics brought laughter and joy to everyone who crossed paths with him</p>
</div>

<div v-click>
- what about a completion for a quiz
  
>e.g. What is the capital of the united kingdom? <p class="text-xs"  style="color:green">What is the population of the united kingdom?<br/>what is the currency of the united kingdom ?</p>

</div>





<div v-click>

- Instruction tuned LLM: `will hopefully return the capital of the United Kingdom is London`
</div>
---


# How to go from a base LLM to a Instruction tuned LLM (e.g: chatgpt)

<br/>

<ul class="ml-6">
  <li v-click style="color:cyan">first train a base LLM on hundreds of billions of words or phrases and more, could take months on large quantum computers</li>
  <li v-click style="color:lightgreen">further train the model by fine-tuning it on a smaller set of examples (where output follows an input instruction)</li>
  <li v-click style="color:green">to further improve, obtain human-ratings of the quality of different LLM outputs, on criteria such as whether it is helpful, honest, harmless etc.</li>
  <li v-click style="color:#097969">further tune LLM to increase probability of generating more highly rated outputs(Using RLHF: Reinforcement learning from human feedback e.g: using other models reward model or prediction penalty model)</li>
</ul>

<!--Notes: 
The training of base LLMs could take months , but from a base LLM to a instruction tuned LLM could be just days with a moderate dataset and moderate compute
-->

---
layout: center
class: text-center
---

# <icomoon-free-lab class="opacity-70"/> [Get started with an LLM](https://github.com/stevengonsalvez/LLM-dojo/blob/main/gpt-api/HLW-1.ipynb) <devicon-jupyter-wordmark/>

<!--
Jupyter: 
A simple, streamlined, document-centric experience, of executing live code


temperature: A temperature of 0 means the responses will be very straightforward, almost deterministic (meaning you almost always get the same response to a given prompt)
A temperature of 1 means the responses can vary wildly.

For transformation tasks (extraction, standardization, format conversion, grammar fixes) prefer a temperature of 0 or up to 0.3.
For writing tasks, you should juice the temperature higher, closer to 0.5. If you want GPT to be highly creative (for marketing or advertising copy for instance), consider values between 0.7 and 1.
-->

---

# Tokens

>Systemically, LLMs does not repeatedly predict the next word , they rather predict the next `token`. Tokens can be words, subwords, characters, symbols etc.

- example: `learning to code is fun`
<div v-click class="text-sm p-2">
<span style="background-color:purple">Learning </span><span style="background-color:green">to </span><span style="background-color:red">code </span><span style="background-color:brown">is </span><span style="background-color:blue">fun</span>
</div>

- example: `Programming is the art of turning caffeine into code`
<div v-click class="text-sm p-2">
<span style="background-color:purple">Program</span><span style="background-color:green">ming </span><span style="background-color:red">is </span><span style="background-color:brown">the </span><span style="background-color:blue">art </span><span style="background-color:red">of </span><span style="background-color:orange">turning </span>
<span style="background-color:purple">caffe</span><span style="background-color:blue">ine </span><span style="background-color:darkgrey">to </span><span style="background-color:violet">code</span>
</div>

- example: Take the word <span style="background-color:green">Gobbledygook</span> and reverse it <icomoon-free-lab class="opacity-70"/> :- [Notebook example](https://github.com/stevengonsalvez/LLM-dojo/blob/main/gpt-api/HLW-1.ipynb) <devicon-jupyter-wordmark/>
<div v-click class="text-sm p-2">
<span style="background-color:red">koogydebbolG</span> : This is Wrong!! - but why ?
</div>

<div v-click class="text-sm p-2">
Token Split:  <span style="background-color:green">["G", "ob", "ble", "dy", "gook"]</span>
</div>

<div v-click class="text-sm p-2">
- Tokens have limits: e.g: 4000 for chatgpt combined between the input (context) and output (completion)
</div>

<div v-click class="text-sm p-2">
<span style="background-color:blue">TIP:</span><span style="color:violet"> next-time when using Chatgpt to cheat on Scrabble, keep this in mind for better outputs</span>
</div>

<!--
Notes: 
- Why tokens
  - Not just English, need to be able to have text generation in multiple languages


>at the end
  - Different models have different limits on the number of tokens (e.g: Anthropic Claude has a 100K context)
  - For English, roughly 1 token is 4 characters or 3/4 of a word (GPT model)
  - The token limits are mainly due to computational constraints, speed, accuracy etc. Processing very long sequences can be memory-intensive and may lead to increased computational complexity
-->

---

# 101s of prompting
<div class="grid grid-cols-2 gap-x-8"><div>

<br/>

![image](https://github.com/stevengonsalvez/LLM-dojo/assets/9320602/f650353b-95e8-4cd7-98e6-00e0b457c03b)


</div><div>


<br/>

```python {2-4|6-7|9-10} {lines:true}
messages =  [  

{'role':'system', 
 'content':"""You are an assistant ...."""},   

{'role':'assistant', 
 'content':"""why is the earth round..."""},

{'role':'user', 
 'content':"""tell me some trivia ..."""},  

] 
```

<br>

<div v-click>

</div>

</div></div>

<Footnotes separator>
  <Footnote><a href="https://github.com/stevengonsalvez/LLM-dojo/blob/main/gpt-api/HLW-1.ipynb" rel="noopener noreferrer">LAB <devicon-jupyter-wordmark/></a></Footnote>
</Footnotes>

<!--
Notes: 
Need to continue with the la

temperature: A temperature of 0 means the responses will be very straightforward, almost deterministic (meaning you almost always get the same response to a given prompt)
A temperature of 1 means the responses can vary wildly.


For transformation tasks (extraction, standardization, format conversion, grammar fixes) prefer a temperature of 0 or up to 0.3.
For writing tasks, you should juice the temperature higher, closer to 0.5. If you want GPT to be highly creative (for marketing or advertising copy for instance), consider values between 0.7 and 1.
-->

---
layout: center
class: text-center
---
# <icomoon-free-lab class="opacity-70"/> [prompting example](https://github.com/stevengonsalvez/LLM-dojo/blob/main/gpt-api/HLW-1.ipynb) <devicon-jupyter-wordmark/>

---

# Building systems with an LLM: Classification

<br/>

> Evaluating Inputs is essential for ensuring the quality and safety of the system

<br/>

- Classify the type of query
- Then use the classification to determine which instructions to use\

<br/>

> How

<br/>

- categorisation
- hard-coded instructions relevant to a category

<br/>

>example

<Footnotes separator>
  <Footnote><a href="https://github.com/stevengonsalvez/LLM-dojo/blob/main/gpt-api/HLW-2.ipynb" rel="noopener noreferrer">LAB <devicon-jupyter-wordmark/></a></Footnote>
</Footnotes>

<!--Notes: 
For instance, in a customer service assistant
- important to first classify the type of user query (e.g: either product information or account information) a
- and then determine the instructions to use based on the classification
- we could use different secondary instruction if the user needs to close an account vs users asking about product information


the delimiter: Is just a  way to separate different parts of an instruction or output. Helps the model determine different sections. 4 hashtags is a nice delimiter as it is a single token
-->
---

# Building Systems with an LLM: Moderation

> If users can input into a system, you would need to ensure the users are using the system responsibly and not trying to abuse it. 

<br/>
<br/>

- Will explore this using OpenAI's [LLM moderation API](https://platform.openai.com/docs/guides/moderation/overview). 
- Will explore protecting against prompt injection

---
title: "Moderation and Prompt Injection"
level: 2
layout: two-cols
---


<span style="color:green" class="text-2xl">Moderation API</span>

<div v-click>

- standard set of usage policies on the content by OPEN AI
- tools that can take identify and filter content that violate
- customisations based on classification rankings
- Free to use. 
- Lets explore an example

</div>

::right::

<span style="color:green" class="text-2xl">Prompt Injection</span>


<div v-click>

- User trying to bypass intended instructions, constraints set by the developer
- e.g: Trying to use a customer service bot to generate blog posts
  
>strategies

- delimiters and clear instructions in the system message
- using additional user prompt instructions to validate intention

- exploration

</div>

<Footnotes separator>
  <Footnote><a href="https://github.com/stevengonsalvez/LLM-dojo/blob/main/gpt-api/HLW-3.ipynb" rel="noopener noreferrer">LAB <devicon-jupyter-wordmark/></a></Footnote>
</Footnotes>

---

# Chain of Thought Reasoning

> * models could rush to results with inaccurate reasoning. So we reframe the query to request steps of reasoning before the model provides the output

<br/>

> * Sometimes it is not appropriate to show the user the reasoning steps (e.g: tutoring apps).
>   * <span style="background-color:purple">Inner monologue</span> is the tactic used to mitigate disclosure

<br/><br/>
<span style="color:green" class="text-2xl">Explore</span>

<Footnotes separator>
  <Footnote><a href="https://github.com/stevengonsalvez/LLM-dojo" rel="noopener noreferrer">LAB <devicon-jupyter-wordmark/></a></Footnote>
</Footnotes>
---

# Chaining Prompts - 1
> * Split complex tasks into a series of simpler subtasks by chaining multiple prompts together. 

<div class="grid grid-cols-2 gap-x-8"><div>
<div v-click>
<br/>
<span style="background-color:red" class="text-sm">- But why can't we just use one prompt and chain of thought?</span><br/> <br/>

- More Focused : efficient management and reduce probability of errors
- chaining prompts is powerful when you have complex workflows to maintain the state of the system at any given point and take different actions depending on the state
  - *Maybe over complicated for something very simple*


</div></div>
<div>
<br/><br/>
<div v-click>
<span style="background-color:green">lets explore with the customer assistant setup</span>


<br/>
<img src="https://github.com/stevengonsalvez/LLM-dojo/assets/9320602/bb532ea8-666a-40d4-a552-b2d508f61710" alt="Italian Trulli">
</div>
</div></div>


<!--Notes: 
We can use the analogy of cooking a complex meal
- managing multiple ingredients, stages , cooking techniques and timings all simultaneously - will be hard to ensure it is cooked properly
- instead of like a recipe, where the focus is on one aspect at a time, focus each part is cooked correctly before moving onto the next

If you take the customer assistant setup we discussed in the previous section, with chaining prompts, you could keep storing the state of where the incoming customer query is classified into, and based on the classification state you could do something different
e.g: in technical support and proceed with relevant instructions from there

- Each subtask only contain instructions required for a single state of the task, which makes 
  - the system easier to manage, 
  - makes sure the model has all information it needs to carry out the task
  - and reduces the likelihood of errors

-->

---

# Chaining Prompts - 2


<br/>

- Reduce costs by Reducing number of tokens used (longer prompts has higher token cost)
- Skip parts of workflow when not needed for a task
- Easier to test (identification of steps that fail more often)
- Ability to include human-in-the-loop
- Allows model to use external tools at certain points in the workflow <span style="color:grey" class="text-sm">(e.g: looking up product catalogue or looking up a calendar) </span>

<br/>
<div v-click>
<span style="background-color:green">What makes a problem complex? </span>

A problem is complex if
- there are many different instructions which could apply to any given situation
- cases where it is complex for the model to reason about the next step
</div>

<Footnotes separator>
  <Footnote><a href="https://github.com/stevengonsalvez/LLM-dojo" rel="noopener noreferrer">LAB <devicon-jupyter-wordmark/></a></Footnote>
</Footnotes>

---

# Output Validation

> To ensure the quality and relevance of the responses, need to validate the output

- Using moderation API on the output
- Using additional prompt steps for validation of the output


<!--Notes: 
-->

<Footnotes separator>
  <Footnote><a href="https://github.com/stevengonsalvez/LLM-dojo" rel="noopener noreferrer">LAB <devicon-jupyter-wordmark/></a></Footnote>
</Footnotes>

---
layout: image
image: https://images.unsplash.com/photo-1468657988500-aca2be09f4c6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2340&q=80
---

# Summary <uim-rocket class="text-sm text-red-400 mx-2" /><uim-rocket class="text-xl text-orange-400 animate-ping" />

- <span style="background-color:green">Process inputs</span>
  - Classify and Moderate

- <span style="background-color:blue">System Instructions</span>
  - Chain of thought
  - Prompt chaining
  - (other techniques to explore) (n-shot prompting, Generated knowledge prompting, least-to-most prompting )

- <span style="background-color:red">Output Validation</span>
  - moderation
  - prompting steps for self validation

---

# Additional notes
<br/>

- Use delimiters like triple backticks (```), angle brackets (<>), or tags (<tag> </tag>) to indicate distinct parts of the input, making it cleaner for debugging and avoiding prompt injection.
- Ask for structured output (i.e. JSON format), this is useful for using the model output for another step.
- Specify the intended tone of the text to get the tonality, format, and length of model output that you need. For example, you can instruct the model to formalize the language, generate not more than 50 words, etc.
- Modify the model’s temperature parameter to play around the model’s degree of randomness. The higher the temperature, the model’s output would be random than accurate, and even hallucinate.


---
