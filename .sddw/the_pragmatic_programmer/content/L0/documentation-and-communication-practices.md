# documentation-and-communication-practices

**Parent:** [[content/L1/developer-pragmatic-principles-communication-design|developer-pragmatic-principles-communication-design]] — Developers must employ second-order thinking, treating natural language as a programming language and applying principles like DRY and ETC, to ensure that all knowledge, including business rules and APIs, has a single, authoritative source representation across code, documentation, and specifications, while tailoring communication pitches to the specific needs of the target audience.

Effective communication is crucial for any developer, as the more effective the communication, the more influential the developer becomes. Documentation is a key area of communication, but developers often fail to give sufficient attention to documentation, frequently treating it merely as an unfortunate necessity or a low-priority task that management might forget at the end of the project. Pragmatic Programmers must embrace documentation as an integral part of the overall development process. When writing documentation, developers can minimize duplication and wasted time by keeping documentation close at hand—directly within the code itself. Consequently, developers should apply all pragmatic principles to documentation, just as they apply to writing code.

**Tip 13: Build Documentation In, Don’t Bolt It On**

While it is relatively easy to generate good-looking documentation from source code comments, the text recommends adding comments to modules and exported functions to assist other developers when they use the code. However, developers should not assume that every function, data structure, type declaration, etc., requires its own comment. Excessive, mechanical comment writing makes maintaining code more difficult because a change requires updating two places. Therefore, developers should restrict non-API commenting to discussing *why* something was done, its purpose, and its goal. Because the source code already shows *how* something is done, commenting on this aspect is redundant, violating the DRY (Don’t Repeat Yourself) principle. Commenting source code provides a perfect opportunity to document elusive project elements that cannot be documented anywhere else, such as engineering trade-offs, the reasoning behind design decisions, or the alternatives that were discarded. 

**Summary Checklist for Communication:**
*   Know what must be communicated.
*   Know the target audience.
*   Choose the appropriate moment.
*   Select a suitable style.
*   Ensure the presentation is visually appealing.
*   Involve the audience in the process.
*   Be a dedicated listener.
*   Follow up with people.
*   Keep both the code and the documentation synchronized.

**Online Communication Standards:**

The principles of communication in writing apply equally to emails, social media posts, and blogs. Email, in particular, is a cornerstone of corporate communications, used for settling disputes, discussing contracts, and serving as evidence in court. Despite this, many people who would not submit a physical paper document are willing to circulate nasty, incoherent emails. Developers must adhere to the following simple rules for online communication:
1.  Proofread before hitting SEND.
2.  Check for spelling errors and look for accidental auto-correct mishaps.
3.  Maintain a simple and clear format.
4.  Keep quotations to a minimum; for example, avoid sending a 100-line email with only 
