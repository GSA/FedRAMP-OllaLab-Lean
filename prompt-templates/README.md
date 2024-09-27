# Prompt Template Making Guide

Prompt templates are systematic repeatable ways to interact with Large Language Models to gain solutions to targeted types of problems. There are at least three ways to use prompt templates.

- The novice templates are simple and usually used to solve simple tasks. For example, you can follow this [Excel Template](https://docs.anthropic.com/en/prompt-library/excel-formula-expert) to ask LLMs to create Excel formulas.

- The programatic templates are probably the most sophisticated with components of: (a) natural languages that serve as prompts, (b) formating instructions, and (c) input parameters. These components can be nested or [composed](https://python.langchain.com/v0.1/docs/modules/model_io/prompts/composition/) in programatic ways, supported by a prompt management platform. An automatic fact checking prompt template can be a good example where there are many layers of follow-up questions. Answers to some questions can be fed to other questions to reach the final conclusion. 

- The third template types may not have complex logics as the second one but requires as many if not more rigors in problem-solving design and hand crafting languages for solving complex problems with LLMs. This folder contains such prompt templates. You can use those templates manually or as part of a prompt template management platform to be composed with other templates to solve even bigger problems.

Because prompt templates can be "programmed" by natural languages, we believe any subject matter experts - like you are - can write great prompt templates for others to use. The following sections will guide you through such process. 

## Before You Start
- Each section may contains lots of details some of which can be irrelevant in some cases while being essential in other cases. Please feel free to customize or even skip an entire section. As long as you end up with a template that can solve a **type** of problem - we salute you.
- Start with the first step and work through them sequentially. The result of each step is generally be "Save to a variable" which can be programatically done or simply be copied and saved to a safe place. The variables represent the entire result texts and when you construct the prompt in the current step, you will have to replace the variables with the entire result texts generated in the previous steps.
- Be prepared to ask follow-up questions or request clarification on the LLM's responses. Do not let yourself be confined by this guide's structure and sample questions.
- Remember that while LLMs can provide valuable insights and ideas, critical thinking and domain expertise are crucial in interpreting and applying their outputs.

## Table of Contents

- [Prompt Template Making Guide](#prompt-template-making-guide)
  - [Before You Start](#before-you-start)
  - [1. Problem Definition Prompt](#1-problem-definition-prompt)
  - [2. Information Gathering Prompts](#2-information-gathering-prompts)
  - [3. Analysis Prompts](#3-analysis-prompts)
  - [4. Solution Generation Prompts](#4-solution-generation-prompts)
    - [4a. Presentation](#4a-presentation)
    - [4b. Business Report](#4b-business-report)
    - [4c. Code Project](#4c-code-project)
    - [4d. Data Conversion Project](#4d-data-conversion-project)
    - [4e. Code Conversion Project](#4e-code-conversion-project)
    - [4f. Data Extraction Project](#4f-data-extraction-project)
    - [4g. Data Generation](#4g-data-generation)
    - [4h. Research Project](#4h-research-project)
  - [5. Evaluation and Solution Selection Prompt](#5-evaluation-and-solution-selection-prompt)
  - [6. Implementation Planning Prompts](#6-implementation-planning-prompts)
  - [7. Evaluation Design Prompt](#7-evaluation-design-prompt)
  - [8. Reflection and Iteration Prompt](#8-reflection-and-iteration-prompt)

## 1. Problem Definition Prompt:
At first, you write a prompt that clearly states the problem and its context. We call this **{{initial problem statement}}**. You may then want to write more prompts to improve it, only when you feel like improvements are needed or the {{initial problem statement}} does not give you the results you want in the later steps.

The template for this section is as follows:
```
I have the following problem statement: {{initial problem statement}}
{{problem statement improvement question}}
```
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
```
I have the following problem statement: {{finalized problem statement}}
{{information gathering question}}
```
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
```
I have the following problem statement: {{finalized problem statement}}
{{gathered information}}
{{analysis prompt}}
```
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

## 4. Solution Generation Prompts:
In this section, we create prompts to brainstorm potential solutions. The template is:
```
I have the following problem statement: {{finalized problem statement}}
{{gathered information}}
{{analysis result}}
{{standards}}
{{constraints}}
{{call for solution}}
```

The {{standards}} variable spells out details for a quality solution. It may include details on expected accuracy, reliability, fairness, inclusivity, and so on. The {{constraints}} variabe states explicit constraints that the solution must follow. The {{call for solution}} variable can be as simple as a sentence. For example, "Generate a list of 10 potential solutions to address the problem. Include both conventional and innovative approaches." The {{call for solution}} variable can also be of multiple sentences as the result of a prompt engineering sub-process. The following sub-sections discuss the process to generate some common types of complex {{call for solution}}.

### 4a. Presentation
Substitute {{call for solution}} with one of the following to generate the targeted part of a presentation.
1. Overall Structure:
"Create a detailed outline for a presentation on [topic], based on the problem statement '[insert problem statement]'. Include main sections and subsections."

2. Introduction:
"Suggest 3-5 engaging ways to open the presentation on [topic] that will capture the audience's attention."

3. Problem Statement:
"Rewrite the following problem statement in a concise, impactful way suitable for a presentation: [insert problem statement]"

4. Background Information:
"List the key pieces of background information that should be included in the presentation about [topic]. Organize these in a logical order."

5. Main Body:
"Based on the analysis results [briefly summarize], what should be the main points covered in the body of the presentation? Provide a structured outline."

6. Data Visualization:
"Suggest 5 types of visual aids (charts, graphs, etc.) that would effectively illustrate the key data points in this presentation."

7. Key Findings:
"Summarize the main findings from the analysis in 3-5 bullet points, suitable for a presentation slide."

8. Recommendations:
"Based on the analysis results, what are the top 3-5 recommendations? Format these as concise, action-oriented statements."

9. Anticipating Questions:
"What are 5-7 potential questions the audience might ask about [topic] after this presentation? How should each be addressed?"

10. Conclusion:
"Craft a strong concluding statement for the presentation that reinforces the main message and motivates the audience to action."

11. Call to Action:
"Suggest an impactful call to action that aligns with the presentation's objectives and findings."

12. Transitions:
"Provide transition sentences or phrases to smoothly connect the following sections of the presentation: [list main sections]"

13. Time Allocation:
"Given a [X]-minute time slot for this presentation, suggest how many minutes should be allocated to each main section of the outline."

14. Audience Engagement:
"Propose 3-5 ways to actively engage the audience during this presentation on [topic]."

15. Executive Summary:
"Create a one-paragraph executive summary of the entire presentation, highlighting the problem, key findings, and main recommendations."

### 4b. Business Report
Substitute {{call for solution}} with one of the following to generate the targeted part of a business report.
1. Overall Structure:
"Create a detailed outline for a business report on [topic], based on the problem statement '[insert problem statement]'. Include main sections and subsections."

2. Executive Summary (this comes early in the report structure but should be generated last):
"Provide a structure for an executive summary that concisely captures the key points of the report on [topic], including the problem, main findings, and recommendations."

3. Introduction:
"Outline an introduction section for a business report on [topic] that sets the context, states the purpose, and provides a brief overview of the report's structure."

4. Problem Statement:
"Rewrite the following problem statement in a clear, concise manner suitable for a formal business report: [insert problem statement]"

5. Background Information:
"List the essential background information that should be included in the report about [topic]. Organize these points in a logical sequence."

6. Methodology:
"Outline a methodology section that explains the approach used to gather and analyze data for this report on [topic]."

7. Findings/Results:
"Based on the analysis results [briefly summarize], structure the main findings section of the report. Include subsections and key points to be covered."

8. Data Presentation:
"Suggest 5-7 types of tables, charts, or graphs that would effectively present the key data points in this business report."

9. Analysis:
"Provide an outline for the analysis section that interprets the findings, identifies trends, and draws insights relevant to [topic]."

10. Discussion:
"Structure a discussion section that explores the implications of the findings, addresses potential limitations, and connects results to the broader context of [topic]."

11. Recommendations:
"Based on the analysis, outline a recommendations section with 3-5 main suggestions. Include subsections for implementation steps and potential impacts."

12. Financial Implications:
"Outline a section that addresses the financial implications of the findings and recommendations, including potential costs, savings, or revenue impacts."

13. Risk Assessment:
"Structure a risk assessment section that identifies potential risks associated with the findings or recommendations, and suggests mitigation strategies."

14. Conclusion:
"Provide an outline for a conclusion that summarizes the key points of the report and reinforces the main message or call to action."

15. Appendices:
"List potential appendices that could provide additional details or supporting information for the main report on [topic]."

16. References:
"Outline how the references section should be structured, including the citation style to be used."

17. Glossary:
"Suggest a structure for a glossary section that defines key terms or acronyms used in the report."

18. Table of Contents:
"Based on the outlined sections, create a detailed table of contents for the business report."

### 4c. Code Project
Substitute {{call for solution}} with one of the following to generate the targeted part of a professional code project.
1. Project Overview:
"Create a high-level outline for a software project that [describe project goal]. Include main components and their purposes."

2. Requirements Specification:
"List the key functional and non-functional requirements for a [type of application] that [describe main functionality]."

3. System Architecture:
"Outline a system architecture for [project name], including main components, their interactions, and any external systems or APIs."

4. Data Model:
"Design a basic data model for [project name]. Include main entities, their attributes, and relationships between entities."

5. API Design:
"Outline the main API endpoints for [project name]. For each endpoint, specify the HTTP method, route, expected input, and output."

6. User Interface (if applicable):
"Describe the main screens or pages for [project name]'s user interface. Include key elements and user interactions for each."

7. Core Algorithms:
"List the core algorithms or data structures that will be central to [project name]. Briefly describe the purpose of each."

8. Technology Stack:
"Suggest an appropriate technology stack for [project name], including programming languages, frameworks, databases, and any other necessary tools."

9. Project Structure:
"Outline a directory structure for [project name], including main folders and their purposes."

10. Testing Strategy:
"Describe a testing strategy for [project name], including types of tests (unit, integration, etc.) and any specific areas requiring extensive testing."

11. Security Considerations:
"List key security considerations for [project name], including potential vulnerabilities and strategies to address them."

12. Performance Optimization:
"Outline potential performance bottlenecks in [project name] and strategies for optimization."

13. Scalability Plan:
"Describe how [project name] can be designed to scale, including considerations for handling increased load or data volume."

14. Deployment Strategy:
"Outline a deployment strategy for [project name], including environments (dev, staging, production) and any CI/CD considerations."

15. Documentation Plan:
"List the types of documentation needed for [project name], including code documentation, API docs, and user manuals."

16. Version Control Strategy:
"Describe a version control strategy for [project name], including branching strategy and commit message conventions."

17. Error Handling and Logging:
"Outline an approach for error handling and logging in [project name], including how errors will be captured, reported, and managed."

18. Third-party Integrations:
"List any third-party services or libraries that [project name] will integrate with, and briefly describe the purpose of each integration."

19. Maintenance and Support:
"Outline a plan for ongoing maintenance and support of [project name] after initial deployment."

20. Code Style and Standards:
"Describe the coding standards and style guidelines to be followed in [project name], including any linting tools or formatters to be used."

### 4d. Data Conversion Project
Substitute {{call for solution}} with one of the following to generate the targeted part of a data conversion project.
1. Project Overview:
"Create a high-level outline for a data conversion project that involves transferring data from [source system] to [target system]. Include main phases and objectives."

2. Source Data Analysis:
"List the key steps for analyzing the source data in [source system], including data profiling, quality assessment, and identifying potential issues."

3. Target System Requirements:
"Outline the data requirements for the target system [target system name]. Include data formats, structures, and any specific constraints or rules."

4. Data Mapping:
"Describe the process for creating a detailed data mapping between [source system] and [target system]. Include considerations for handling discrepancies or incompatibilities."

5. Data Cleansing Strategy:
"Outline a strategy for cleansing and standardizing the data from [source system] before conversion. Include common data quality issues to address."

6. Transformation Rules:
"List the main data transformation rules needed to convert data from [source system] format to [target system] format. Include examples of complex transformations."

7. Validation Checks:
"Describe the validation checks that should be implemented to ensure data integrity during and after the conversion process."

8. Error Handling:
"Outline an approach for handling errors and exceptions during the data conversion process. Include strategies for logging, reporting, and resolving issues."

9. Testing Strategy:
"Create an outline for a comprehensive testing strategy for the data conversion project, including unit testing, integration testing, and user acceptance testing."

10. Performance Optimization:
"Suggest strategies for optimizing the performance of the data conversion process, especially for handling large volumes of data."

11. Rollback Plan:
"Describe a rollback plan in case the data conversion encounters critical issues. Include steps to revert to the original state."

12. Data Reconciliation:
"Outline a process for reconciling data between the source and target systems to ensure completeness and accuracy of the conversion."

13. Security and Privacy Considerations:
"List key security and privacy considerations for handling sensitive data during the conversion process. Include compliance requirements if applicable."

14. Conversion Tools and Technologies:
"Suggest appropriate tools and technologies for implementing the data conversion project, considering the specific requirements of [source system] and [target system]."

15. Project Timeline:
"Create a high-level project timeline for the data conversion, breaking down the process into main phases with estimated durations."

16. Resource Requirements:
"Outline the resource requirements for the data conversion project, including personnel, hardware, and software needs."

17. Stakeholder Communication Plan:
"Describe a plan for communicating project progress, issues, and milestones to key stakeholders throughout the conversion process."

18. Post-Conversion Verification:
"Outline a strategy for verifying the success of the data conversion after completion, including key metrics and acceptance criteria."

19. Documentation Requirements:
"List the types of documentation needed for the data conversion project, including technical specifications, user guides, and handover documents."

20. Training Plan:
"Describe a training plan for users of the new system, focusing on any changes in data structure or access methods resulting from the conversion."

21. Maintenance and Support:
"Outline a plan for ongoing maintenance and support after the data conversion, including handling any residual issues or data discrepancies."

22. Compliance and Auditing:
"Describe how the data conversion process will adhere to relevant compliance requirements and how it will be audited for accuracy and completeness."

### 4e. Code Conversion Project
Substitute {{call for solution}} with one of the following to generate the targeted part of a code conversion project.
1. Project Overview:
"Create a high-level outline for a code conversion project that involves migrating from [source language/framework] to [target language/framework]. Include main phases and objectives."

2. Source Code Analysis:
"List the key steps for analyzing the existing codebase in [source language/framework], including structure assessment, identifying dependencies, and potential conversion challenges."

3. Target Platform Requirements:
"Outline the requirements and constraints of the target platform [target language/framework]. Include language features, libraries, and any specific architectural considerations."

4. Code Mapping Strategy:
"Describe the process for mapping code constructs from [source language] to [target language]. Include handling of language-specific features and idioms."

5. Dependency Management:
"Outline a strategy for managing and converting external dependencies. Include considerations for finding equivalent libraries in the target ecosystem."

6. Architecture Adaptation:
"Describe how the overall architecture might need to be adapted when moving from [source framework] to [target framework]. Include potential design pattern changes."

7. Database Interaction Conversion:
"If applicable, outline the approach for converting database interactions, including ORM changes, query adaptations, and data access patterns."

8. API Conversion:
"Describe the strategy for converting APIs, including changes in request/response handling, authentication methods, and error management."

9. User Interface Conversion (if applicable):
"Outline the approach for converting the user interface, including framework-specific components, styling, and state management."

10. Testing Strategy:
"Create an outline for a comprehensive testing strategy, including unit test conversion, integration testing, and ensuring feature parity."

11. Performance Optimization:
"Suggest strategies for optimizing the performance of the converted code, considering the strengths and best practices of [target language/framework]."

12. Code Style and Standards:
"Describe how to adapt the code to follow best practices and coding standards of [target language/framework]."

13. Refactoring Opportunities:
"Outline a process for identifying and implementing refactoring opportunities during the conversion process."

14. Automated Conversion Tools:
"Suggest potential automated tools or scripts that could assist in the code conversion process. Describe their benefits and limitations."

15. Manual Conversion Guidelines:
"Provide guidelines for manual code conversion, including how to handle complex or language-specific features that can't be automatically converted."

16. Incremental Conversion Strategy:
"Describe an approach for incrementally converting the codebase, if applicable. Include strategies for maintaining a working system during conversion."

17. Version Control Strategy:
"Outline a version control strategy for the conversion process, including branching strategy and how to manage parallel development."

18. Build and Deployment Adaptation:
"Describe how build processes and deployment pipelines need to be adapted for the new [target language/framework]."

19. Performance Benchmarking:
"Outline a plan for benchmarking performance before and after conversion to ensure maintained or improved efficiency."

20. Documentation Update Plan:
"List the types of documentation that need to be updated or created as part of the conversion process."

21. Team Training Plan:
"Describe a plan for training the development team on [target language/framework], including key areas of focus and potential resources."

22. Code Review Process:
"Outline a code review process specific to the conversion project, including what to look for and how to ensure quality in the converted code."

23. Rollback Strategy:
"Describe a rollback strategy in case critical issues are encountered during or after the conversion."

24. Post-Conversion Optimization:
"Outline steps for post-conversion optimization, including leveraging new language/framework features for improved performance or maintainability."

25. Compliance and Security Review:
"Describe how to ensure the converted codebase meets all necessary compliance and security requirements."

### 4f. Data Extraction Project
Substitute {{call for solution}} with one of the following to generate the targeted part of a data extraction project.
1. Project Overview:
   "Create a high-level outline for a data extraction project that involves extracting data from [source(s)]. Include main phases and objectives."

2. Source Analysis:
   "List the key steps for analyzing the data source(s) [specify sources], including structure, format, and potential extraction challenges."

3. Data Mapping:
   "Outline a process for mapping the required data fields from the source(s) to the target schema or format."

4. Extraction Method:
   "Describe the most appropriate extraction method(s) for [source type], considering factors like data volume, update frequency, and source system impact."

5. Data Validation Rules:
   "List essential data validation rules to ensure the quality and integrity of extracted data."

6. Error Handling Strategy:
   "Outline an approach for handling errors during the extraction process, including logging, reporting, and resolution procedures."

7. Performance Optimization:
   "Suggest strategies for optimizing the performance of the data extraction process, especially for large volumes of data."

8. Incremental Extraction Plan:
   "If applicable, describe an approach for implementing incremental data extraction to minimize processing time and resource usage."

9. Data Transformation Requirements:
   "List any necessary data transformations that need to be applied during or immediately after extraction."

10. Output Format Specification:
    "Specify the required output format(s) for the extracted data, including file types, structure, and any specific formatting requirements."

11. Scheduling and Automation:
    "Outline a plan for scheduling and automating the extraction process, including frequency and trigger mechanisms."

12. Security and Privacy Considerations:
    "Describe security measures to protect sensitive data during extraction, transfer, and storage. Include compliance requirements if applicable."

13. Data Lineage Tracking:
    "Suggest methods for tracking data lineage to maintain transparency about the data's origin and transformations."

14. Metadata Management:
    "Outline a strategy for capturing and managing metadata associated with the extracted data."

15. Quality Assurance Plan:
    "Create a comprehensive QA plan for the extraction process, including data accuracy, completeness, and consistency checks."

16. Performance Metrics:
    "List key performance indicators (KPIs) to measure the success and efficiency of the data extraction process."

17. Scalability Considerations:
    "Describe how the extraction process can be designed to scale for increasing data volumes or additional data sources."

18. Integration with Downstream Systems:
    "Outline how the extracted data will be integrated with or made available to downstream systems or processes."

19. Monitoring and Alerting:
    "Suggest a monitoring and alerting strategy to ensure timely detection and response to extraction issues or failures."

20. Documentation Requirements:
    "List the types of documentation needed for the data extraction project, including technical specifications, user guides, and data dictionaries."

21. Compliance and Auditing:
    "Describe how the extraction process will adhere to relevant compliance requirements and how it will be audited."

22. Change Management Process:
    "Outline a process for managing changes to the extraction requirements or source data structures over time."

23. Testing Strategy:
    "Create an outline for a testing strategy, including unit testing, integration testing, and end-to-end testing of the extraction process."

24. Rollback and Recovery Plan:
    "Describe a rollback and recovery plan in case of critical failures during or after the extraction process."

25. Training and Knowledge Transfer:
    "Outline a plan for training team members and transferring knowledge about the extraction process and its maintenance."

### 4g. Data Generation
Substitute {{call for solution}} with one of the following to generate the targeted part of a data generation project.
1. Project Overview:
   "Create a high-level outline for a data generation project that aims to produce [type of data] for [purpose]. Include main phases and objectives."

2. Data Requirements Analysis:
   "List the key steps for analyzing and defining the requirements for the generated data, including volume, variety, and specific characteristics."

3. Data Model Design:
   "Outline the process for designing a data model that will guide the generation of realistic and consistent data."

4. Data Generation Methodology:
   "Describe the most appropriate methodology or approach for generating the required data, considering factors like randomness, patterns, and relationships."

5. Data Sources for Reference:
   "Identify potential reference data sources that can inform or validate the generated data to ensure realism and accuracy."

6. Data Validation Rules:
   "List essential validation rules to ensure the generated data meets quality standards and mimics real-world scenarios accurately."

7. Scalability Planning:
   "Outline strategies for ensuring the data generation process can scale to produce large volumes of data efficiently."

8. Performance Optimization:
   "Suggest approaches for optimizing the performance of the data generation process, especially for creating large datasets."

9. Data Diversity and Edge Cases:
   "Describe methods for ensuring the generated data includes a diverse range of scenarios, including edge cases and anomalies."

10. Relationship and Dependency Modeling:
    "Outline how relationships and dependencies between different data elements will be modeled and maintained in the generated dataset."

11. Temporal Data Considerations:
    "If applicable, describe how time-based patterns or historical trends will be incorporated into the generated data."

12. Personally Identifiable Information (PII) Handling:
    "Outline the approach for handling PII in the generated data, including anonymization or synthetic PII generation techniques."

13. Data Format Specifications:
    "Specify the required output format(s) for the generated data, including file types, structure, and any specific formatting requirements."

14. Reproducibility and Seeding:
    "Describe methods for ensuring reproducibility of the generated data, including the use of seeds for random number generation."

15. Quality Assurance Plan:
    "Create a comprehensive QA plan for the data generation process, including statistical analysis and comparison with real-world data distributions."

16. Integration with Test Environments:
    "Outline how the generated data will be integrated with or made available to test environments or systems."

17. Data Generation Tools Selection:
    "Suggest appropriate tools or frameworks for implementing the data generation process, considering the specific requirements of the project."

18. Customization and Configurability:
    "Describe how the data generation process can be made customizable and configurable to adapt to changing requirements."

19. Documentation Requirements:
    "List the types of documentation needed for the data generation project, including technical specifications, user guides, and data dictionaries."

20. Version Control and Change Management:
    "Outline a strategy for version control of the data generation scripts/code and managing changes to data generation requirements over time."

21. Performance Metrics:
    "List key performance indicators (KPIs) to measure the efficiency and effectiveness of the data generation process."

22. Compliance and Legal Considerations:
    "Describe how to ensure the generated data complies with relevant regulations and legal requirements, especially if mimicking sensitive or regulated data."

23. Data Storage and Management:
    "Outline a plan for storing, managing, and potentially distributing the generated datasets."

24. Automation and Scheduling:
    "Describe how the data generation process can be automated and scheduled for regular updates or on-demand execution."

25. Training and Knowledge Transfer:
    "Outline a plan for training team members on using and maintaining the data generation system."

### 4h. Research Project
Substitute {{call for solution}} with one of the following to generate the targeted part of a research project.
1. Project Overview:
   "Create a high-level outline for a research project on [topic]. Include main phases and objectives."

2. Research Question Formulation:
   "Develop 3-5 potential research questions related to [topic], ensuring they are specific, measurable, and significant to the field."

3. Literature Review Structure:
   "Outline the structure for a comprehensive literature review on [topic], including key areas to cover and potential sources."

4. Theoretical Framework:
   "Describe potential theoretical frameworks that could be applied to the study of [topic]. Explain how each might inform the research."

5. Methodology Design:
   "Outline appropriate research methodologies for investigating [topic], considering both quantitative and qualitative approaches."

6. Data Collection Methods:
   "List and briefly describe suitable data collection methods for researching [topic], including their strengths and limitations."

7. Sampling Strategy:
   "Describe potential sampling strategies for the study, including sample size considerations and selection criteria."

8. Ethical Considerations:
   "Outline the key ethical considerations for conducting research on [topic], including potential risks and mitigation strategies."

9. Data Analysis Plan:
   "Suggest appropriate data analysis techniques for the collected data, including statistical methods or qualitative analysis approaches."

10. Validity and Reliability:
    "Describe strategies to ensure the validity and reliability of the research findings, including potential threats and how to address them."

11. Timeline and Milestones:
    "Create a high-level project timeline for the research, breaking down the process into main phases with estimated durations and key milestones."

12. Resource Requirements:
    "Outline the resource requirements for the research project, including personnel, equipment, software, and potential funding needs."

13. Potential Limitations:
    "Identify potential limitations or challenges of the proposed research and suggest ways to address or acknowledge them."

14. Interdisciplinary Connections:
    "Explore potential interdisciplinary connections or collaborations that could enhance the research on [topic]."

15. Innovation and Originality:
    "Describe how this research project could contribute new knowledge or innovative approaches to the study of [topic]."

16. Dissemination Plan:
    "Outline a strategy for disseminating the research findings, including potential publication venues and conference presentations."

17. Stakeholder Engagement:
    "Identify key stakeholders for this research and describe how they might be engaged throughout the project."

18. Risk Assessment:
    "Conduct a risk assessment for the research project, identifying potential risks and mitigation strategies."

19. Quality Assurance Measures:
    "Describe quality assurance measures to be implemented throughout the research process to ensure rigorous and reliable results."

20. Data Management Plan:
    "Outline a data management plan for the research, including data storage, security, and sharing considerations."

21. Pilot Study Design:
    "If applicable, describe a potential pilot study to test and refine the research methodology before full implementation."

22. Funding Proposal Outline:
    "Create an outline for a funding proposal for this research project, including key sections and points to emphasize."

23. Collaboration Plan:
    "If relevant, outline a plan for collaboration with other researchers or institutions, including roles and responsibilities."

24. Impact Assessment:
    "Describe methods for assessing the potential impact of the research, both within the academic field and in practical applications."

25. Future Research Directions:
    "Suggest potential future research directions or follow-up studies that could build on this project."

## 5. Evaluation and Solution Selection Prompt:
This step is for the cases where you have multiple solutions and you need to pick the best one.
   - "For each of the proposed solutions to the problem, list the pros and cons. Consider feasibility, resource requirements, and potential impacts."
   - "Rank the proposed solutions from most promising to least promising. Explain your reasoning for each ranking."
   - "Based on the evaluation, which solution appears to be the most effective for addressing the problem? Provide a detailed justification for this choice."

Prompts for formal evaluation and selection strategies are:
1. Comprehensive Comparison:
   "Create a detailed comparison matrix for the following solutions: [list solutions]. Include key criteria such as effectiveness, cost, feasibility, and potential risks."

2. Pros and Cons Analysis:
   "For each of the proposed solutions [list solutions], provide a comprehensive list of pros and cons. Ensure the analysis covers short-term and long-term implications."

3. Alignment with Objectives:
   "Evaluate how well each solution [list solutions] aligns with the primary objectives of [state project/problem]. Rank them in order of alignment and explain your reasoning."

4. Resource Requirements:
   "Analyze the resource requirements (time, money, personnel, technology) for implementing each solution [list solutions]. Which solution offers the best balance of impact and resource efficiency?"

5. Risk Assessment:
   "Conduct a risk assessment for each solution [list solutions]. Identify potential risks, their likelihood, and potential impact. Which solution presents the most manageable risk profile?"

6. Stakeholder Impact:
   "Assess the potential impact of each solution [list solutions] on key stakeholders. Which solution offers the most positive overall impact across all stakeholder groups?"

7. Implementation Complexity:
   "Evaluate the complexity of implementing each solution [list solutions]. Consider factors such as technical challenges, organizational changes, and potential resistance. Rank the solutions from least to most complex to implement."

8. Scalability and Flexibility:
   "Analyze the scalability and flexibility of each solution [list solutions]. Which option is best suited to adapt to future changes or growth?"

9. Cost-Benefit Analysis:
   "Perform a cost-benefit analysis for each solution [list solutions]. Which solution offers the best return on investment in both short and long term?"

10. Sustainability:
    "Assess the long-term sustainability of each solution [list solutions]. Consider factors such as ongoing maintenance, future relevance, and environmental impact."

11. Innovation and Competitive Advantage:
    "Evaluate each solution [list solutions] in terms of innovation and potential competitive advantage. Which solution offers the most unique or forward-thinking approach?"

12. Compliance and Legal Considerations:
    "Review each solution [list solutions] for compliance with relevant regulations and legal requirements. Are there any solutions that pose compliance risks?"

13. Cultural Fit:
    "Assess how well each solution [list solutions] aligns with the organization's culture and values. Which option is most likely to be embraced by the team/organization?"

14. Time to Value:
    "Analyze the expected time to realize value for each solution [list solutions]. Which option offers the quickest path to achieving the desired outcomes?"

15. Synergy with Existing Systems:
    "Evaluate how well each solution [list solutions] integrates with existing systems and processes. Which option offers the smoothest integration?"

16. Expert Opinion Synthesis:
    "Synthesize expert opinions on each solution [list solutions]. Based on this synthesis, which solution emerges as the most favored by subject matter experts?"

17. Quantitative Scoring:
    "Develop a quantitative scoring system for evaluating the solutions [list solutions] based on key criteria [list criteria]. Apply this scoring system and rank the solutions."

18. Scenario Testing:
    "Apply each solution [list solutions] to various potential future scenarios. Which solution performs best across different possible futures?"

19. Ethical Considerations:
    "Evaluate each solution [list solutions] from an ethical standpoint. Are there any ethical concerns or advantages associated with specific solutions?"

20. Holistic Impact Assessment:
    "Conduct a holistic assessment of each solution [list solutions], considering all factors discussed. Based on this comprehensive evaluation, which solution emerges as the best overall choice? Provide a detailed justification for this selection."

> [!NOTE]
> The result of this section is saved to {{solution}}

## 6. Implementation Planning Prompts:
In this section, we create prompts to craft implementation planning details. By using implementation planning prompts with LLMs, project managers can gain valuable insights and detailed plans that enhance the likelihood of successful project execution. However, it's important to remember that while LLMs can provide comprehensive suggestions, human expertise and judgment are crucial in refining and implementing these plans in real-world contexts.

The template is:
```
I have the following problem statement: {{finalized problem statement}}
{{standards}}
{{constraints}}
{{solution}}
{{call for implementation planning}}
```

The {{call for implementation planning}} can be any of the following:
   - "Outline a step-by-step implementation plan for the chosen solution to the problem. Include timelines and resource requirements for each step."
   - "What potential obstacles might arise during the implementation of this solution? Suggest strategies to overcome each obstacle."
   - "For each objective, list the specific tasks required to achieve it. Ensure each task is concrete and actionable."
   - "Organize the tasks for each objective in a logical sequence. Identify any dependencies between tasks."
   - "Create a timeline for the action plan, assigning estimated start and end dates for each task. Consider realistic timeframes and potential constraints."
   - "Assign responsibilities for each task. Identify who will be accountable, responsible, consulted, and informed (RACI matrix)."
   - "Define key milestones throughout the action plan. Explain how each milestone contributes to the overall goal."

The result of this section is saved to {{Implementation plan}}

## 7. Evaluation Design Prompt:
The evaluation design serves as a crucial link between the planning insights provided by the LLM and the real-world execution and impact of the project. It ensures that the project's implementation aligns with its intended goals and that there's a systematic way to measure its success and learn from the process.it's important to remember that while LLMs can provide valuable input, human expertise is crucial in tailoring the evaluation design to the specific context of the project and interpreting the results effectively. 

The template is:
```
I have the following problem statement: {{finalized problem statement}}
{{standards}}
{{constraints}}
{{solution}}
{{call for evaluation}}
```

The {{call for evaluation}} can be any of the following:
1. Evaluation Purpose:
   "Clearly define the purpose and objectives of the evaluation for [project/program/initiative]. What specific questions should this evaluation answer?"

2. Evaluation Criteria:
   "Identify the key criteria for evaluating [project/program/initiative]. For each criterion, provide a brief description and its importance."

3. Evaluation Framework:
   "Suggest an appropriate evaluation framework or model for [project/program/initiative]. Explain why this framework is suitable."

4. Stakeholder Identification:
   "Identify all relevant stakeholders for this evaluation. For each stakeholder group, describe their interest in and potential contribution to the evaluation process."

5. Data Collection Methods:
   "List and describe appropriate data collection methods for this evaluation. Consider both quantitative and qualitative approaches."

6. Data Sources:
   "Identify potential data sources for the evaluation. Include both existing data and new data that needs to be collected."

7. Sampling Strategy:
   "If applicable, outline a sampling strategy for data collection. Consider sample size, selection criteria, and representativeness."

8. Timeline Development:
   "Create a timeline for the evaluation process, including key phases and milestones. Consider any time constraints or deadlines."

9. Resource Allocation:
   "Identify the resources required for this evaluation (e.g., personnel, budget, tools). Specify any resource constraints or special requirements."

10. Ethical Considerations:
    "Outline the ethical considerations for this evaluation. Include issues such as informed consent, confidentiality, and potential risks to participants."

11. Data Analysis Plan:
    "Describe the data analysis methods to be used in the evaluation. Include both quantitative and qualitative analysis techniques as appropriate."

12. Evaluation Team:
    "Define the roles and responsibilities within the evaluation team. What skills and expertise are required?"

13. Quality Assurance Measures:
    "Outline quality assurance measures for the evaluation process. How will you ensure the reliability and validity of the findings?"

14. Reporting Strategy:
    "Describe the reporting strategy for the evaluation findings. Consider different formats and audiences for the results."

15. Utilization Plan:
    "Develop a plan for how the evaluation findings will be utilized. How will results be incorporated into decision-making processes?"

16. Baseline Data:
    "If relevant, describe how baseline data will be established or utilized in the evaluation process."

17. Performance Indicators:
    "Identify key performance indicators (KPIs) that will be used to measure the success or impact of [project/program/initiative]."

18. Comparative Analysis:
    "If applicable, describe how the evaluation will compare results to benchmarks, standards, or similar projects/programs."

19. Cost-Effectiveness Analysis:
    "Outline a method for assessing the cost-effectiveness of [project/program/initiative] as part of the evaluation."

20. Challenges and Limitations:
    "Identify potential challenges or limitations in the evaluation process. How will these be addressed or acknowledged?"

21. Participatory Evaluation Elements:
    "Describe any participatory elements in the evaluation process. How will stakeholders be involved beyond just providing data?"

22. Technology and Tools:
    "Specify any technology or tools required for data collection, analysis, or reporting in this evaluation."

23. Evaluation Capacity Building:
    "If relevant, outline a plan for building evaluation capacity within the organization or among stakeholders."

24. Dissemination Plan:
    "Develop a plan for disseminating the evaluation findings. Include target audiences, methods, and timelines."

25. Meta-Evaluation:
    "Describe how the quality and effectiveness of the evaluation itself will be assessed (meta-evaluation)."

26. Sustainability Assessment:
    "If applicable, outline how the evaluation will assess the sustainability of [project/program/initiative] outcomes."

27. Adaptive Management:
    "Describe how the evaluation process will support adaptive management of [project/program/initiative]. How will interim findings be used?"

28. Cultural Sensitivity:
    "Outline measures to ensure cultural sensitivity and appropriateness in the evaluation process, especially if working with diverse populations."

The result of this section is saved to {{Evaluation plan}}

## 8. Reflection and Interation Prompt (if necessary):
In essence, reflection prompts serve as a critical bridge between the capabilities of LLMs and the nuanced, context-specific needs of real-world problem-solving and project execution. They ensure that the use of LLMs remains thoughtful, adaptive, and aligned with broader project goals and ethical considerations. For example, we can prompt "Reflect on the problem-solving process we've used. What are the strengths and weaknesses of this approach? How could it be improved for future complex problems?"

In the context of LLMs, iteration is not just about repeating the same process, but about intelligently refining and expanding the approach based on accumulated insights. It's a powerful tool for navigating the complexities of real-world problems, ensuring that the final solution is not just theoretically sound, but practically effective and well-adapted to its intended context. For example, we can prompt "Given what we've learned so far, how should we reframe or adjust our approach to the problem? Suggest specific modifications to our problem-solving strategy."