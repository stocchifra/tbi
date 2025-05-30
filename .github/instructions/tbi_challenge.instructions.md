---
applyTo: '**'
---
Summary 

This technical test evaluates a candidate's ability to develop an AI-based application. Candidates will be asked to demonstrate skills in running inference on trained Large Language Models, designing ad developing a full-stack application, leveraging containerisation, testing methodology, documentation, and performance optimization to meet latency requirements and resource constraints. The challenge focuses on processing and extracting insights from natural language textual data, requiring candidates to balance technical implementation with user experience considerations while maintaining cost efficiency and ensuring system stability under continuous use. 

 

Task 

Create a prototype application that automates the analysis of documents, extracting key insights and generating summaries. 

 

Functional requirements 

The application runs in one of the popular browsers (Chrome, Edge, Safari) 
The user can either Upload or copy-paste a simple text document (text only, utf-8 encoded) into the chat window 
The user interacts with the system using natural language queries, e.g. “Can you summarize what dropout is and how it is used in deep learning” 
The user can see the chat history - their prompts and application responses 
Any error is clearly communicated in the UI and does not crash the application 
If the application requires any API keys, it offers a UI to input such a key and does not require any configuration files or environment variables to be set 
Non functional requirements 

p95 for a round-trip query processing is 3 seconds 
that is the time measured from the moment the user runs the query, until the first words of the response are displayed 
the application may require an internet connection - if it does, and it’s not present, the user should be clearly notified about the fact 
p99 hardware requirements: 16 GB RAM, 16 GB VRAM, 4 CPU cores, 10 GB HDD 
p99 of the aggregate cost of using any external APIs required to run a single query is 0.01$  
p99 stability is 100 queries without any errors (which also include external rate limiter errors) 


I want to use Openai responses api to do that 
and the following frameworks:
