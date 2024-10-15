# Basic Code Testing Templates
Software testing largely includes two main branches. We will use PyTest as the framework for automated testing. 

## Exploratory testing
Template 1
> You are a software engineer and tester who is curious and loves looking for edge cases.
> I have the following {{code language}} codes:
>
> {{the codes to test}}
>
> Please explore it and find any issues that might cause bugs or poor functionality.

## Functional Testing
These templates make sure the targeted program perform well according to specified functional requirements. In other words, functional tests ensure each function of the program does work as expected.
### Unit Tests
> Write unit tests for the {{function/class/module}} in {{programming language}}.
> The {{function/class/module}} is responsible for {{brief description of the functionality}}.
> Ensure that all edge cases, typical use cases, and error conditions are tested.
> Use {{testing framework}} for the tests.
### Integration Tests
> Generate integration tests for the {{system component/module/service}} that interacts with {{other system components/services}}.
> The goal is to verify that these components interact correctly according to {{expected behavior or functionality}}.
> Use {{programming language}} and {{testing framework}}.
> Ensure all data flows and API calls are validated for both success and failure scenarios.
### System Tests
> Create system tests for the entire {{application/system}} to verify that it works as a whole.
> The system consists of {{list major components/services/modules}}.
> Focus on verifying that the interactions between these components perform as expected.
> Test the functionality of key features such as {{describe key system features}} using {{programming language}} and {{testing framework}}.
### Acceptance Tests
> Write acceptance tests to validate whether the {{software application/system}} meets the defined requirements and user expectations.
> Focus on testing {{key features/functionalities}} from the user's perspective.
> Ensure tests reflect real-world use cases and include both positive and negative scenarios.
> Use {{testing framework}} to implement these tests.

## Non-functional Testing
### Security Tests
> Generate security tests to evaluate potential vulnerabilities in {{application/system}}.
> Test for common security issues such as SQL injection, cross-site scripting (XSS), authentication, authorization flaws, and data leaks.
> The tests should target both front-end and back-end vulnerabilities and include tests for secure handling of {{sensitive data, API keys, etc.}}.
> Use {{security testing tool/framework}}.
### Performance Tests
> Create performance tests to assess the speed, scalability, and stability of {{application/system}} under load.
> The tests should simulate real-world usage patterns, such as {{specific user actions}} and measure response time, throughput, and resource utilization.
> Also, include stress tests to evaluate the system’s behavior under extreme load conditions.
> Use {{performance testing tool/framework}}.
### Usability Tests
> Develop usability tests for {{application/system}} to evaluate the user experience.
> These tests should focus on ease of navigation, clarity of the user interface, responsiveness, and accessibility.
> The tests should cover scenarios like {{user completing a specific task/interaction}} and include metrics such as time to complete tasks and error rates.
> Use {{usability testing tool}} for testing.
### Compatibility Tests
> Generate compatibility tests for {{application/system}} to ensure it works across different {{browsers, operating systems, devices, etc.}}.
> The tests should verify that all features behave consistently on {{list of environments}}.
> Include tests for both functionality and UI/UX across these platforms.
> Use {{compatibility testing tool/framework}}.

## Automated Testing
tba
