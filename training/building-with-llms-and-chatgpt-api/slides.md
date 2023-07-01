---
theme: academic
class: text-white
colorSchema: dark
coverAuthor: Alexander Eble
coverAuthorUrl: https://alexeble.de
coverBackgroundUrl: https://images.unsplash.com/photo-1607799279861-4dd421887fb3
coverBackgroundSource: unsplash
coverBackgroundSourceUrl: https://unsplash.com/photos/8qEB0fTe9Vw
coverDate: 12/01/2022
exportFilename: dev-environment-as-code
favicon: https://alexeble.mo.cloudinary.net/logo.png
fonts:
  local: Monserrat, Roboto Mono
hideInToc: true
info: |
  Engineer with LLMS
lineNumbers: true
titleTemplate: '%s • Alexander Eble'
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
  <a href="https://github.com/slidevjs/slidev" target="_blank" alt="GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

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

layout: figure
figureCaption: Delimitation Containers in Development and Production
figureFootnoteNumber: 1
figureUrl: https://containers.dev/img/dev-container-stages.png

---

<Footnotes separator>
  <Footnote number=1><a href="https://containers.dev/img/dev-container-stages.png" rel="noopener noreferrer">Microsoft</a></Footnote>
</Footnotes>

---

# Motivation

Dev Containers facilitate

<ul class="ml-6">
  <li>documentation</li>
  <li>setup</li>
  <li>sharing</li>
  <li>compatibility</li>
  <li>encapsulation</li>
  <li>prototyping</li>
  <li>device independency</li>
  <li>Continuous Integration</li>
</ul>

---

layout: center
class: text-center

---

# Prerequisites

[Docker](https://www.docker.com/) · [VS Code](https://code.visualstudio.com/) · [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

# Simple Dev Container

[.devcontainer.json or .devcontainer/devcontainer.json](https://containers.dev/implementors/json_reference/)

```json {2|3|4-14|15|16}
{
  "name": "dev-environment-as-code",
  "image": "node",
  "customizations": {
    "vscode": {
      "extensions": [
        "antfu.slidev",
        "editorconfig.editorconfig",
      ],
      "settings": {
        "editor.formatOnSave": true
      }
    }
  },
  "forwardPorts": [3030],
  "postStartCommand": "npm install && npm run dev",
}
```

---

layout: figure
figureCaption: Open with Dev Containers Extension
figureUrl: /command-palette.png

---

---

# Advanced Dev Container

Image customization

```json
{
  "build": {
    "dockerfile": "Dockerfile",
  },
}
```

Container orchestration

```json
{
  "dockerComposeFile": "docker-compose.yml",
  "service": "server",
  "workspaceFolder": "/usr/src/server"
}
```

<div class="mt-6">
  <p>
    <mdi-arrow-right /> <a href="https://github.com/alexanderdavide/dev-environment-as-code/tree/master/app" rel="noopener noreferrer">Example</a>
    with server, database and VS Code customization
  </p>
</div>

---

# Disadvantages and Limitations

Dev Containers

<ul class="ml-6">
  <li>might have lower performance</li>
  <li>consume a lot of storage for images</li>
  <li>utilize a lot of network bandwith to load images</li>
  <li>might cause projects to loose Host OS compatibility</li>
  <li>might be technically impractical or impossible for certain projects</li>
</ul>

---

# Outlook

<ul>
  <li><a href="https://github.com/codespaces" rel="noopener noreferrer">GitHub Codespaces</a></li>
  <li><a href="https://github.com/recode-sh/cli" rel="noopener noreferrer">recode</a></li>
  <li><a href="https://www.gitpod.io/" rel="noopener noreferrer">GitPod</a>, <a href="https://stackblitz.com/" rel="noopener noreferrer">StackBlitz</a> etc.</li>
  <li><a href="https://devenv.sh/" rel="noopener noreferrer">devenv</a></li>
</ul>
---
theme: academic
class: text-white
colorSchema: dark
coverAuthor: Alexander Eble
coverAuthorUrl: https://alexeble.de
coverBackgroundUrl: https://images.unsplash.com/photo-1607799279861-4dd421887fb3
coverBackgroundSource: unsplash
coverBackgroundSourceUrl: https://unsplash.com/photos/8qEB0fTe9Vw
coverDate: 12/01/2022
exportFilename: dev-environment-as-code
favicon: https://alexeble.mo.cloudinary.net/logo.png
fonts:
  local: Monserrat, Roboto Mono
hideInToc: true
info: |
  Engineer with LLMS
lineNumbers: true
titleTemplate: '%s • Alexander Eble'
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
  <a href="https://github.com/slidevjs/slidev" target="_blank" alt="GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

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

# How does LLM work

> You are probably familiar with the text generation process, likely completions given a prompt

<div class="mt-8">
  <ul>
    <li v-click><q>I love eating</q></li>
    <li v-click><q>full-featured</q></li>
    <li v-click><q>specification</q></li>
    <li v-click><q>enrich existing formats</q></li>
    <li v-click><q>as coding environments or for continuous integration and testing</q></li>
  </ul>
</div>

<Footnotes separator>
  <Footnote number=1><a href="https://containers.dev/" rel="noopener noreferrer">Microsoft</a></Footnote>
</Footnotes>

---

# How does LLM work

> A Development Container (or Dev Container for short) allows you to use a container as a full-featured development environment. The Development Containers Specification seeks to find ways to enrich existing formats with common development specific settings, tools, and configuration [..] so that they can be used as coding environments or for continuous integration and testing.<sup>1</sup>

<div class="mt-8">
  <ul>
    <li v-click><q>container</q> <logos-docker-icon /></li>
    <li v-click><q>full-featured</q></li>
    <li v-click><q>specification</q></li>
    <li v-click><q>enrich existing formats</q></li>
    <li v-click><q>as coding environments or for continuous integration and testing</q></li>
  </ul>
</div>

<Footnotes separator>
  <Footnote number=1><a href="https://containers.dev/" rel="noopener noreferrer">Microsoft</a></Footnote>
</Footnotes>

---

layout: figure
figureCaption: Delimitation Containers in Development and Production
figureFootnoteNumber: 1
figureUrl: https://containers.dev/img/dev-container-stages.png

---

<Footnotes separator>
  <Footnote number=1><a href="https://containers.dev/img/dev-container-stages.png" rel="noopener noreferrer">Microsoft</a></Footnote>
</Footnotes>

---

# Motivation

Dev Containers facilitate

<ul class="ml-6">
  <li>documentation</li>
  <li>setup</li>
  <li>sharing</li>
  <li>compatibility</li>
  <li>encapsulation</li>
  <li>prototyping</li>
  <li>device independency</li>
  <li>Continuous Integration</li>
</ul>

---

layout: center
class: text-center

---

# Prerequisites

[Docker](https://www.docker.com/) · [VS Code](https://code.visualstudio.com/) · [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

# Simple Dev Container

[.devcontainer.json or .devcontainer/devcontainer.json](https://containers.dev/implementors/json_reference/)

```json {2|3|4-14|15|16}
{
  "name": "dev-environment-as-code",
  "image": "node",
  "customizations": {
    "vscode": {
      "extensions": [
        "antfu.slidev",
        "editorconfig.editorconfig",
      ],
      "settings": {
        "editor.formatOnSave": true
      }
    }
  },
  "forwardPorts": [3030],
  "postStartCommand": "npm install && npm run dev",
}
```

---

layout: figure
figureCaption: Open with Dev Containers Extension
figureUrl: /command-palette.png

---

---

# Advanced Dev Container

Image customization

```json
{
  "build": {
    "dockerfile": "Dockerfile",
  },
}
```

Container orchestration

```json
{
  "dockerComposeFile": "docker-compose.yml",
  "service": "server",
  "workspaceFolder": "/usr/src/server"
}
```

<div class="mt-6">
  <p>
    <mdi-arrow-right /> <a href="https://github.com/alexanderdavide/dev-environment-as-code/tree/master/app" rel="noopener noreferrer">Example</a>
    with server, database and VS Code customization
  </p>
</div>

---

# Disadvantages and Limitations

Dev Containers

<ul class="ml-6">
  <li>might have lower performance</li>
  <li>consume a lot of storage for images</li>
  <li>utilize a lot of network bandwith to load images</li>
  <li>might cause projects to loose Host OS compatibility</li>
  <li>might be technically impractical or impossible for certain projects</li>
</ul>

---

# Outlook

<ul>
  <li><a href="https://github.com/codespaces" rel="noopener noreferrer">GitHub Codespaces</a></li>
  <li><a href="https://github.com/recode-sh/cli" rel="noopener noreferrer">recode</a></li>
  <li><a href="https://www.gitpod.io/" rel="noopener noreferrer">GitPod</a>, <a href="https://stackblitz.com/" rel="noopener noreferrer">StackBlitz</a> etc.</li>
  <li><a href="https://devenv.sh/" rel="noopener noreferrer">devenv</a></li>
</ul>
