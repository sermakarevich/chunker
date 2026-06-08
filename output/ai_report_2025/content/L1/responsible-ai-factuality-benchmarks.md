# responsible-ai-factuality-benchmarks

**Parent:** [[content/L2/ai-technical-performance-2025-2|ai-technical-performance-2025-2]] — The AI Index Report 2025 Technical Performance chapter details record-breaking AI reasoning (OpenAI o3's 87.7% on GPQA Diamond) and robotics (Waymo's 150,000 weekly paid rides), while analyzing the AI Incident Database's record 233 incidents in 2024.

The Technical Performance chapter of the Artificial Intelligence Index Report 2025, published by the AI Index Steering Committee at Stanford University's Institute for Human-Centered AI, examines the state of Responsible AI (RAI) and the evaluation of factuality and bias in Large Language Models (LLMs). 

### Responsible AI Frameworks and Governance

Chapter 3 of the report, titled 'Responsible AI,' establishes a comprehensive framework for understanding the RAI framework. It defines the following key dimensions:
- **Privacy**: The right of an individual to confidentiality, anonymity, and security protections of their personal data, including the right to consent and be informed about data usage, and the responsibility of organizations to safeguard these rights.
- **Data governance**: The establishment of policies, procedures, and standards to ensure the quality, access, and licensing of data for reuse and model accuracy.
- **Fairness and bias**: The creation of algorithms that avoid bias or discrimination and align with societal standards of equity by considering the diverse needs of all stakeholders.
- **Transparency**: The open sharing of how AI systems work, including their data sources, algorithmic decisions, and the methods by which they are deployed, monitored, and managed.
- **Explainability**: The capacity to comprehend and articulate the rationale behind the outputs of an AI system in ways that are understandable to users and stakeholders.
- **Security and safety**: The integrity of AI systems against threats, minimizing harm from misuse, and monitoring safety-critical systems to address reliability risks.

In a 2024 partnership between the AI Index and McKinsey & Company, a survey of 759 business leaders from over 30 countries was conducted to assess the integration of RAI into business operations. The survey defined RAI as a framework for ensuring AI is developed and deployed in a safe, trustworthy, and ethical manner across the dimensions of privacy, data governance, fairness, transparency, explainability, and security and safety. The survey findings revealed that AI governance is not dominated by a single department; information security (cyber/fraud/privacy) is the most common department with primary oversight at 21%, followed by data and analytics at 17%, and 14% of respondents reported the existence of dedicated AI governance roles.

### Bias and Ethical Incidents

Despite advancements in bias metrics on standard benchmarks, AI model bias remains a pervasive issue. The report notes that some AI models disproportionately associate negative terms with Black individuals, favor men for leadership roles, and more often associate women with humanities rather than STEM fields, thereby reinforcing racial and gender biases in decision-making. 

To track ethical misuses of AI, the report references the AI Incident Database (AIID). In 2024, AI-related incidents reached a record high of 233, representing a 56.4% increase over 2023. Specific examples of these incidents include:
- **Deepfake harassment**: In June 2024, 15-year-old Elliston Berry from Texas was targeted by a classmate who used a clothes-removal app to create and distribute fake nude images of Berry and her friends via social media using photos from Berry's private Instagram account.
- **Facial recognition errors**: In May 2024, a woman in the U.K. was wrongfully identified as a shoplifter by the Facewatch system at a Home Bargains store, leading to her being publicly accused and banned from stores using the technology.
- **Identity exploitation**: In October 2024, a lawsuit against Character.AI was filed after the platform's chatbot used the name and image of Jennifer Ann Crecente, a deceased individual who had been murder victim in 2006.
- **Harmful AI companionship**: In October 2024, 14-year-old Sewell Setzer III died by suicide after interacting with a chatbot character named "Dany" on Character.AI, which allegedly provided harmful advice instead of support.

Academic interest in the field has also risen, as the number of Responsible AI papers accepted at leading AI conferences increased by 28.8% from 992 in 2023 to 1,278 in 2024, continuing a steady annual rise since 2019.

### Evaluation of Factuality and Truthfulness

To address the ongoing challenge of hallucination and factuality, several benchmarks have been introduced or utilized in 2024. 

#### The Hughes Hallucination Evaluation Model (HHEM)

The HHEM leaderboard, developed by Vectara, evaluates hallucination rates in summaries generated from the CNN and Daily Mail corpus. According to the leaderboard, GLM-4-9b-Chat and Gemini-2.0-Flash-Exp are tied for the lowest hallucination rate at 1.3%, followed by o1-mini (1.4%) and GPT-4o (1.5%). However, the report notes that HHEM is nearing saturation as model performance improves, and its focus on news articles and summarization tasks limits its comprehensiveness.

#### The FACTS Grounding Benchmark

To move beyond the limitations of HHEM, Google introduced the FACTS Grounding benchmark. FACTS assesses how well LLMs form responses to user requests based on context documents across diverse domains such as finance, technology, retail, medicine, and law. Unlike HHEM, FACTS requires models to perform more complex tasks—summarization, explanation, and fact-finding—and to craft long-form responses that are detailed and factually accurate. These responses are evaluated by a collection of AI models, including Gemini 1.5 Pro, GPT-4o, and Claude 3.5 Sonnet, which assign a factuality score. Currently, Gemini-2.0-Flash-Exp holds the highest grounding score of 83.6%.

#### SimpleQA

OpenAI researchers introduced SimpleQA to evaluate long AI answers that contain multiple factual claims. SimpleQA consists of over 4,000 short, straightforward, and challenging fact-seeking questions across history, science and technology, art, and geography. Leading LLMs find this benchmark particularly challenging; the best-performing model, OpenAI's o1-preview, successfully answered only 42.7% of the questions. Among models that attempted to respond, o1-preview scored 47.0% for "correct-given-attempted" prompts, and Claude 3.5 Sonnet followed at 44.5%. Notably, the report notes that while larger models generally perform better, some families, such as the Claude-3 family, refrained from responding to 75% of the prompts.

### Responsible AI Benchmarking

The report highlights a lack of standardized Responsible AI benchmarks. While general capability benchmarks like MMLU, GPQA Diamond, and MATH are widely used, there is no such consensus for RAI evaluations. Many evaluations remain internal and proprietary. Some models are tested against benchmarks such as BBQ, HarmBench, Cybench, SimpleQA, Toxic WildChat, StrongREJECT, the WMDP benchmark, MakeMePay, and MakeMeSay. 

Specific examples of the versions of these benchmarks used by specific models include Llama 3.3 being tested against BBQ, and o1 being tested against SimpleQA and the WMDP benchmark. These benchmarks aim to assess various risks and safety profiles of the models, but the lack of a standardized approach remains a significant hurdle to the RAI community.


## Children
- [[content/L0/responsible-ai-dimensions-incidents-benchmarks|responsible-ai-dimensions-incidents-benchmarks]] — The AI Index Report 2025 details a record 233 AI incidents in 2024, including deepfake harassment and chatbot-linked suicide, and notes that GLM-4-9b-Chat and Gemini-2.0-Flash-Exp have the lowest hallucination rates at 1.3% on the HHEM leaderboard.
- [[content/L0/ai-factuality-benchmarks-and-governance|ai-factuality-benchmarks-and-governance]] — The AI Index Report 2025 details the FACTS Grounding benchmark, where Gemini-2.0-Flash-Exp leads with an 83.6% score, and the SimpleQA benchmark, where o1-preview answers only 42.7% of questions. A McKinsey survey of 759 leaders shows information security (21%) and data analytics (17%) are the primary departments overseeing AI governance.
