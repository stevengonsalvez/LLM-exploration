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
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

---
layout: new-section
---
# Agenda

<div class="font-mono grid grid-cols-3 gap-4">
  <div class="bg-gray-500/50 px-3 py-2 rounded w-full" v-click>
    <h4>Part 1</h4>
    <p class="text-center">How LLMs work, how they are trained</p>
    <p class="text-center">Language Models, Chatformat, tokens</p>
    <p class="text-center">Classification</p>
    <p class="text-center">Moderation</p>
    <p class="text-center">Chain of thought reasoning</p>
  </div>
  <div class="bg-gray-500/50 px-3 py-2 rounded w-full" v-click>
    <h4>Part 2</h4>
    <div class="bg-gray-500/50 mb-2 mt-4 p-2 rounded w-50"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 mt-4 rounded p-2 w-50"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 mt-4 rounded p-2 w-50"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 mt-4 rounded p-2 w-50"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
  </div>
  <div class="bg-gray-500/50 px-3 py-2 rounded w-full" v-click>
    <h4>Part 3</h4>
    <div class="bg-gray-500/50 mb-2 mt-4 p-2 rounded w-50"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 mt-4 rounded p-2 w-50"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 mt-4 rounded p-2 w-50"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 rounded p-2 w-full"></div>
    <div class="bg-gray-500/50 mb-2 mt-4 rounded p-2 w-50"></div>
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


---

# How does LLM work - 2

> Supervised Learning ( A -> B). A computer learns an input -> output mapping using labelled data.

<br/>

<div v-click>

<p class="text-sm"  style="color:green"> > example of labelled data for sentiments</p>

| Input                    | output   |
| ------------------------ | -------- |
| The pizza was delicious  | positive |
| The service was poor     | negative |
| The ambience was awesome | positive |

</div>

---

# How does LLM work - 3


> LLMs are built using supervised learning to repeatedly predict the next word. 

<p class="text-sm"  style="color:green">"My favorite hobby is"</p>
<div v-click class="text-sm p-4">

| Input                                       | output         |
| ------------------------------------------- | -------------- |
| My favorite                                 | hobby is       |
| My favorite hobby is                        | playing        |
| My favorite hobby is playing the            | guitar         |
| My favorite hobby is playing the guitar and | creating music | 
</div>

---

# Types of LLMS

> - Base LLM
> - Instruction tuned LLMs

<br/>

- Base LLM
  - Predicts next word based on training data

>e.g. Once there was a Goat named Oliver<p class="text-xs"  style="color:green">whose mischievous antics brought laughter and joy to everyone who crossed paths with him</p>

- what about a completion for a quiz
>e.g. what is the capital of the united kingdom?<p class="text-xs"  style="color:green">what is the united kingdoms population? <br/> what is the currency of the united kingdom ?</p>

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

- example: Take the word <span style="background-color:green">Gobbledygook</span> and reverse it
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

<!--Notes: 
- Why tokens
  - Not just English, need to be able to have text generation in multiple languages
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

> for example, 

---
layout: center
class: text-center
---
# <icomoon-free-lab class="opacity-70"/> [Example](https://github.com/stevengonsalvez/LLM-dojo/blob/main/gpt-api/HLW-1.ipynb) <devicon-jupyter-wordmark/>

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
---

# Chain of Thought Reasoning

> * models could rush to results with inaccurate reasoning. So we reframe the query to request steps of reasoning before the model provides the output

<br/>

> * Sometimes it is not appropriate to show the user the reasoning steps (e.g: tutoring apps).
>   * Inner monologue is the tactic used to mitigate disclosure


---

# SPLIT section

> * Dapr Component - Bindings - [MQTT](https://docs.dapr.io/reference/components-reference/supported-bindings/mqtt/)


---