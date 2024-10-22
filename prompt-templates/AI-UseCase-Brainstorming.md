# AI Use Case Brainstorming Template
This template will allow effective brainstorming sessions for AI Use Cases with an AI collaborator.

## 1. Problem Definition Prompt:
At first, you write a prompt that clearly states the problem and its context. We call this **{{initial problem statement}}**. You may then want to write more prompts to improve it, only when you feel like improvements are needed or the {{initial problem statement}} does not give you the results you want in the later steps.

The template for this section is as follows:
>
> I have the following problem statement: {{initial problem statement}}
>
> Please help me improve the problem statement considering the following questions:
>{{problem statement improvement question}}
>

The **{{problem statement improvement question}}** can be any mix of the following questions:
- "What are the key components and aspects of the problem statement?"
- "What potential ambiguities or unclear elements exist in the current problem statement?"
- "Who are the main stakeholders affected by or involved in the problem? How might each stakeholder perceive the problem differently?"
- "What historical context or background information is crucial for understanding the problem?"
- "Are there any recent developments or trends that have significantly impacted the problem?"
- "What should be included in the scope of the problem, and what elements should be explicitly excluded?"
- "What are the key constraints or limitations that need to be considered when defining the problem?"
- "How can we frame the problem in a way that allows for clear measurement of progress or resolution?"
- "How might the problem be viewed differently from various disciplinary perspectives (e.g., economic, social, technological, environmental)?"
- "What contrasting viewpoints exist regarding the nature or importance of the problem?"
- "What assumptions are we making about the problem that might need to be challenged or verified?"
- "Are there any hidden biases in how we're currently thinking about the problem?"
- "How can we reframe the problem in a way that focuses on [an objective] rather than just challenges?"
- "What other problems or challenges are closely related to or influenced by the problem?"
- "How does the problem fit into larger systemic issues or trends?"
- "How can we make the problem statement more specific and actionable?"
- "What aspects of the problem are most critical or urgent to address?"

Final synthesis and refinement:
- "Based on all the information discussed, can you propose a refined, comprehensive problem statement for the problem?"

We save the answers to the final systhesis & refinement question to the variable **{{finalized problem statement}}**

## 2. Information Gathering Prompts:
In the context of using LLMs, information gathering prompts are particularly important because they help focus the model's vast knowledge on the specific problem at hand. The quality of our problem-solving is often directly related to the quality and comprehensiveness of the information we gather at the outset. Therefore, crafting effective information gathering prompts is a critical skill in leveraging LLMs for complex problem-solving.

The template for this section is as follows:
>
>I have the following problem statement: {{finalized problem statement}}
>
>{{information gathering question}}
>
The {{finalized problem statement}} is Section 1's result. The **{{information gathering question}}** can be any mix of the following questions:

- "What are the key factors contributing to the problem? Provide a comprehensive list with brief explanations."
- "Summarize the most recent research findings related to the problem."Comprehensive Overview:
- "Provide a detailed overview of the problem, including its history, current state, and future projections. Structure your response with clear headings and subheadings."
- "Identify and describe the main stakeholders involved in the problem. For each stakeholder, explain their role, interests, and potential impact on the situation."
- "What are the primary factors contributing to the problem? For each factor, provide a brief explanation and, if possible, cite relevant research or data."
- "Outline the historical development of the problem over the past [X] years. Highlight key events, turning points, and trends that have shaped its current state."
- "Outline the current regulatory framework surrounding the problem. Include relevant laws, policies, and governing bodies at local, national, and international levels if applicable."
- "Describe how recent technological advancements have impacted or are likely to impact the problem in the near future. Consider both positive and negative potential effects."
- "Analyze the economic dimensions of the problem, including costs, benefits, market dynamics, and potential economic consequences of addressing or not addressing the problem."

We save the answers to the variable **{{gathered information}}**

## 3. Analysis Prompts:
By using well-crafted analysis prompts, we can harness the LLM's processing power to gain a deeper, more nuanced understanding of the problem. This enhanced understanding is crucial for developing effective solutions and making informed decisions in complex problem-solving scenarios.

The template for this section is as follows:
>
>I have the following problem statement: {{finalized problem statement}}
>
>{{gathered information}}
>
>{{analysis prompt}}
>
The {{finalized problem statement}} is Section 1's result. The {{gathered information}} is section 2's result. The **{{analysis prompt}}** can be any mix of the following:
- "What are the potential root causes of the problem? Please provide a detailed analysis for each."
- "How might these root causes be interconnected or influence each other?"
- "Perform a SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis for [situation/organization] in relation to [problem]. Provide detailed explanations for each point."
- "Analyze the trends related to [problem/issue] over the past [X] years. Identify key patterns, inflection points, and potential future trajectories."
- "Apply systems thinking to [problem]. Identify the key elements of the system, their interactions, feedback loops, and potential leverage points for intervention."
- "Conduct a cost-benefit analysis of addressing [problem]. Consider both tangible and intangible costs and benefits, and analyze short-term versus long-term implications."
- "Perform a risk assessment related to [problem/issue]. Identify potential risks, evaluate their likelihood and potential impact, and suggest possible mitigation strategies."
- "Develop three potential future scenarios related to [problem/issue]: best-case, worst-case, and most likely. For each scenario, describe key factors and potential outcomes."
- "Create a causal loop diagram for [problem/issue]. Identify key variables, their relationships, and feedback loops. Explain how these interactions contribute to the overall dynamics of the situation."
- "Conduct a cross-impact analysis of the factors influencing [problem/issue]. Identify how changes in one factor might affect others, and describe potential cascading effects."
- "Analyze the ethical implications of [problem/issue or proposed solution]. Consider different ethical frameworks and potential conflicts between stakeholder interests."
- "Analyze historical attempts to address similar problems to [current issue]. What approaches were tried, what were the outcomes, and what lessons can be applied to the current situation?"
- "Identify and analyze the key constraints (e.g., resources, regulations, technology) affecting [problem/issue]. For each constraint, explain its impact and potential ways to work within or overcome it."

We save the answers to the variable **{{analysis result}}**

## 4. Potential AI Use Case Generation Prompts:
In this section, we create prompts to brainstorm potential AI use cases. The template is:
>
>I have the following problem statement: {{finalized problem statement}}
>
>{{gathered information}}
>
>{{analysis result}}
>
>{{constraints}}
>
>Please give me a list of AI-based use cases that can help solve the problem.
>
The {{constraints}} variabe states explicit constraints that the solution must follow.

## 5. Generate the Selected AI Use Case
In this section, we create prompts to craft our selected AI use cases. The assumption is we may have some ideas about our targeted use case. However, we may want to incorporate some details from the recommended use cases as well. The template is:
>
>The title of my use case is:
>{{Use case title}}
>
>Please write a use case description that incorporates the following details:
>
>{{original use case details}}
>
>and the details from your proposed use case number {{AI proposed use case number(s)}}
>
>Make sure the description is {{use case description constraints}}
>
{{Use case title}} is your intended title for the use case. {{original use case details}} is your initial draft description of your intended use case. {{AI proposed use case number(s)}} are the numbers of AI proposed use cases in the earlier step. If AI didn't use numbers to label the use cases, make sure you repeat the earlier step and explicitly instruct the AI to put numbers in the use case. If you believe you have a solid use case description, you can skip this step.

We save the final use case details to the variable **{{Use case details}}**

## 6. Generate the Purpose
>{{Use case title}}
>
>{{Use case details}}
>
>{{gathered information}}
>
>{{analysis result}}
>
>Give me a one or two sentence description of the system's intended purposes.
>
The results will be saved to the variable **{{Intended Purposes}}**

## 7. Generate the Benefits
>{{Use case title}}
>
>{{Use case details}}
>
>{{gathered information}}
>
>{{analysis result}}
>
>{{Intended Purposes}}
>
>Give me some powerful benefits that the system can deliver
>
The results will be saved to the variable **{{Benefits}}**

## 8. Generate Measures and Metrics
>{{Use case title}}
>
>{{Use case details}}
>
>{{Intended Purposes}}
>
>{{Benefits}}
>
>What are the recommended measures and metrics to actualy measure the benefits?
>
The results will be saved to the variable **{{Measures}}**

## 9. Threat Modeling
In this section, we create prompts to generate threat model, mitigation, proper uses and best practices for the AI use cases. First, we generate the threat model
>
>{{Use case title}}
>
>{{Use case details}}
>
>{{Intended Purposes}}
>
>Present a threat model of the system that will be used for this use case. The key assumptions are {{assumptions}}. The threat model should have common components per industry standards such as asset identification, threats, risks, how attackers can cause damage or abuse the system, etc.
>
The result will be saved into the variable **{{Threat Model}}**

We might want to drill down further to certain risks

>
>{{Use case title}}
>
>{{Use case details}}
>
>{{Intended Purposes}}
>
>{{Threat Model}}
>
>Tell me more about risks associated with {{drill down criteria}}

Examples of {{drill down criteria}} can be "underserved communities", "vulnerable population", etc. The result will be saved to the variable **{{Drilled down threat model}}**

Next, we generate the mitigations.
>
>{{Use case title}}
>
>{{Use case details}}
>
>{{Intended Purposes}}
>
>{{Threat Model}}
>
>{{Drilled down threat model}}
>
>Please give me migitation strategies and best practices in dealing with the identified threats.
>
The result will be saved into the variable **{{Mitigations}}**

## 10. Identify Impacted Stakeholders
We will manually identify the content of a new variable {{stake holders}} which will contain information about the stake holders such as their business division, their business functions, etc.panda
>
>{{Use case title}}
>
>{{Use case details}}
>
>{{Intended Purposes}}
>
>The stake holders are:
>{{stake holders}}
>
>{{Threat Model}}
>
>{{Drilled down threat model}}
>
>Identify all potential related variables in and outside of the system's scopes and show me how the stakeholders can be impacted by potential threats.
>

The result will be saved into the variable **{{Impacts}}**
