# ai-index-2025-technical-performance-and-landscape

**Parent:** [[content/L2/ai-index-2025-technical-performance-economics|ai-index-2025-technical-performance-economics]] — The 2025 AI Index Report details record-breaking AI performance, such as OpenAI o3 achieving 87.7% on GPQA Diamond and 87.5% on ARC-AGI, alongside the deployment of Waymo's 150,000 weekly paid robotaxi rides and the expansion of AI's strategic economic integration.

The 2025 Artificial Intelligence Index Report, published by the AI Index Steering Committee at Stanford University's Institute for Human-Centered AI, provides a comprehensive analysis of AI model performance, talent distribution, and the global AI landscape. 

### Technical Performance and Benchmarking

AI models have shown record-breaking progress in coding, mathematics, and general reasoning. In coding, the LMSYS Chatbot Arena for LLMs coding filter shows that among Chinese models, DeepSeek-V3 leads with an Elo score of 1,317, though it trails the highest-ranking model by 3.8%.

Mathematical problem-solving is tracked through several benchmarks. The GSM8K benchmark, consisting of 8,000 grade-school math word problems, has seen a top performance of 97.72% by a Claude Sonnet 3.5 variant optimized with HPT prompting, surpassing the 2023 high of 91.00%. However, saturation is evident as several models from Mistral, Meta, and Qwen scored around 96% in 2024. For competition-level mathematics, the MATH dataset (12,500 problems) saw OpenAI's o3-mini (high) achieve a record score of 97.9% in January 2025, exceeding the human baseline of 90%.

To address benchmark saturation, Epoch AI introduced FrontierMath, focusing on number theory, real analysis, algebraic geometry, and category theory. While Gemini 1.5 Pro initially performed best, it only solved 2.0% of the problems; however, OpenAI's o3 model is reported to have scored 25.2% on FrontierMath.

In theorem proving, Google DeepMind's AlphaProof and AlphaGeometry 2 were used for the 2024 International Mathematical Olympiad (IMO). Together, they solved four out of six problems; AlphaProof handled two algebra problems and one number theory problem, while AlphaGeometry 2 solved the geometry problem in 24 seconds. AlphaGeometry's performance on the IMO-AG-30 benchmarking set (25 out of 30 problems) exceeds that of a typical IMO silver medalist (22.9 problems).

General intelligence and reasoning are evaluated via the MMMU benchmark (11,500 college-level questions). As of January 2025, OpenAI's o1 scored 78.2%, improving on the 2024 state-of-the-art (SOTA) of 59.4%, though it remains below the human expert baseline of 82.6%. For multisubject reasoning, the GPQA benchmark (448 expert-crafted questions) shows a massive leap: GPT-4 scored 38.8% in 2023, while OpenAI's o3 achieved a SOTA score of 87.7% by December 2024, finally surpassing the human validator baseline of 81.3%.

To test generalization, the ARC-AGI benchmark was used. In 2020, the top score was 20%; by 2024, it rose to 33%. OpenAI's o3 achieved 75.7%, and with a high compute budget exceeding the benchmark's $10,000 limit, it reached 87.5%.

To combat saturation across MMLU and GSM8K, Humanity's Last Exam (HLE), containing 2,700 multimodal questions, was introduced. Initial results are low: OpenAI's o1 scores 8.8%, Gemini 2.0 Flash Thinking (7.2%), Gemini 1.5 Pro (5.2%), Claude 3.5 Sonnet (4.8%), Grok-2 (3.9%), and GPT-4o (3.1%). Experts suggest performance may exceed 50% by late 2025.

### Planning and Agentic Capabilities

In planning (reasoning about world-altering actions), the PlanBench suite (600 problems) shows OpenAI's o1 scoring 97.8% in Blocksworld zero-shot evaluation, compared to Llama 3.1 405B (62.6%) and GPT-4o (35.5%). In the harder Mystery Blocksworld domain, o1 scored 52.8%, while Llama 3.1 405B scored 0.8% and GPT-4 scored 0%. However, o1 still only solves 23.6% of planning instances requiring 20+ steps.

RE-Bench evaluates R&D capabilities in seven machine learning research environments. In short-term (two-hour) settings, AI systems score four times higher than human experts. However, in 32-hour budget settings, humans outperform AI by a factor of two. AI agents excel in specific tasks like writing custom Triton kernels.

General AI assistants are tested via the GAIA benchmark (466 questions). GPT-4 with plugins initially answered only 15% (humans scored 92%). By 2024, the top system reached 65.1%, a ~30 percentage point increase over 2023.

AI agents (autonomous systems) are tested via VisualAgentBench (VAB). GPT-4o achieved the highest overall success rate at 36.2%, while most proprietary models averaged around 20%.

### Robotics and Autonomous Motion

In the Robot Learning Benchmark (RLBench), SAM2Act (a collaboration between the University of Washington, Universidad Católica San Pablo, Nvidia, and the Allen Institute for AI) achieved an 86.8% success rate as of January 2025, a 2.8 percentage point increase over 2024 and a 66.7 percentage point increase from 2021.

Humanoid robotics grew significantly in 2024. Figure AI's Figure 02 stands 5'6\

## Children
- [[content/L0/ai_talent_investment_workforce_impact|ai_talent_investment_workforce_impact]] — The provided text discusses the dynamics of AI talent migration, investment trends, and the dual nature of AI's impact on the workforce, where it acts as both an augmentative tool and a driver of automation for repetitive tasks.
- [[content/L0/ai_investment_and_deployment_trends|ai_investment_and_deployment_trends]] — Private investment in AI rose until 2023, primarily driven by generative AI, which is now being deployed in sectors like software development and marketing with an increasing focus on ethics and transparency.
- [[content/L0/system_error_report.json|system_error_report.json]] — The user encountered a technical error in the previous interaction and is requesting a corrected response in the valid JSON format according to the same schema as the previous request.
