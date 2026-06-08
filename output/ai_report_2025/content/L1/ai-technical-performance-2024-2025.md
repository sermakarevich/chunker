# ai-technical-performance-2024-2025

**Parent:** [[content/L2/ai-index-2025-technical-ecosystem-synthesis|ai-index-2025-technical-ecosystem-synthesis]] — The AI Index Report 2025 highlights a shift in AI research and patent leadership toward East Asia and the Pacific, alongside a convergence in performance between US and Chinese models, and a significant decrease in inference costs for GPT-3.5 equivalent models from $20 to $0.07 per million2024.

The Technical Performance chapter of the Artificial Intelligence Index Report 2025, published by the AI Index Steering Committee at Stanford University's Institute for Human-Centered AI, provides an extensive analysis of AI technical progress in 2024. The report outlines a landscape characterized by the rapid mastery of new benchmarks, the convergence of frontier model performance, and a shrinking gap between open-weight and closed-weight models, as well as between US-based and Chinese models. 

### AI Performance Trends and Convergence
AI systems are mastering new benchmarks at an unprecedented pace. For tests introduced in 2023 to push the limits of AI, performance gains by 2024 were remarkable: MMMU saw an increase of 18.8 percentage points, and GPQA saw a 48.9 percentage point increase. On SWE-bench, AI ability to solve coding problems leaped from 4.4% in 2023 to 71.7% in 2024. In areas where humans still lead, the gap is closing; for instance, the state-of-the-art AI systems are now 7.9 percentage points ahead of human performance on the MATH benchmark for competition-level mathematics, compared to a 0.3-point gap in 2024. On the MMMU benchmark for multidisciplinary expert-level questions, the 2024 model o1 scored 78.2%, just 4.4 percentage points below the human benchmark of 82.6%.

There is a clear trend of performance convergence at the frontier. The Elo score difference between the top-ranked and 10th-ranked models on the LMSYS Chatbot Arena Leaderboard narrowed from 11.9% (as reported in the previous AI Index) to 5.4% by early 2025. Furthermore, the difference between the top two models shrank from 4.9% in 2023 to 0.7% in 2024. Current top providers include OpenAI, Google, Anthropic, Meta, Mistral AI, DeepSeek, and xAI.

### Open-Weight vs. Closed-Weight Models
The gap between closed-weight and open-weight models has narrowed significantly. In early January 2024, the leading closed-weight model outperformed the top open-weight model by 8.04% (or 8.0%) on the Chatbot Arena Leaderboard, but by February 2025, this gap shrank to 1.70% (or 1.7%). On the MMLU benchmark, closed-weight models led open models by 15.9 percentage points in late 2023, but this difference fell to 0.1 percentage point by the end of 2024. This shift was largely driven by the release of Meta's Llama 3.1 and DeepSeek's V3.

Models are categorized by their level of openness. Entirely closed models include Google's Med-Gemini. Limited access models, provided via API but without released weights, include OpenAI's GPT-4o and Anthropic's Claude 3.5. Open-weight models, where weights are available for modification, include Meta's Llama 3.3 and Stable Video 4D. While open-weight models are more accessible, they are not strictly 'open source' because training data and underlying code are often withheld. Advocates argue they prevent monopolies and spur innovation—citing the use of Llama in military applications and the creation of Meditron—while critics warn of security risks, such as the creation of bioweapons or disinformation.

### Global Competition: US vs. China
The technical performance gap between the US and China is closing. In January 2024, the top US model outperformed the best Chinese model by 9.3% on the LMSYS Chatbot Arena, but by February 2025, the gap was 1.7%. At the end of 2023, the performance gaps on MMLU, MMMU, MATH, and HumanEval were 17.5, 13.5, 24.3, and 31.6 percentage points, respectively. By the end of 2024, these gaps narrowed to 0.3, 8.1, 1.6, and 3.7 percentage points. The launch of DeepSeek-R1 was particularly notable as it achieved these results using only a fraction of the hardware resources typically required, casting doubt on the effectiveness of US semiconductor export controls.

### Model Efficiency and Compact Models
While scaling has driven progress, 2024 saw a breakthrough in smaller, high-performing models, including Llama 3.1 8B, o1-mini, GPT-4o mini, Gemini 2.0 Flash, and Mistral Small 3.5. These compact models offer higher algorithmic efficiency, lower training costs, and faster inference. This is exemplified by the MMLU benchmark: in 2022, the smallest model to score over 60% was PaLM (540 billion parameters); by 2024, Microsoft's Phi-3-mini achieved this with only 3.8 billion parameters, a 142-fold reduction in size.

### Reasoning Paradigms and Agentic AI
New reasoning paradigms, specifically test-time compute and iterative reasoning, have improved performance. OpenAI's o1 and o3 models use these techniques. The o1 model scored 74.4% on an International Mathematical Olympiad qualifying exam, whereas GPT-4o scored 9.3%. However, o1 is nearly six times more expensive and 30 times slower than GPT-4o. 

AI agents are showing early promise. The 2024 launch of RE-Bench provides a rigorous benchmark for agents. In short time-horizon settings (two-hour budget), top AI systems score four times higher than human experts. However, in 32-hour budget settings, humans still outscore AI two to one. AI agents already match human expertise in specific tasks like writing Triton kernels, operating at lower costs and higher speeds.

### Benchmarking Challenges and the Turing Test
Benchmarks are essential but flawed. The BetterBench study analyzed 24 benchmarks and found 14 failed to report statistical significance, 17 lacked replication scripts, and most had poor documentation. In Figure 2.1.41 of the report, MMLU showed poor adherence to quality standards, while GPQA performed better. Contamination—where models are trained on test questions—is a common issue, specifically noted in many LLMs' performance on the GSM8K mathematics benchmark. To combat this, LiveBench was introduced to provide periodically updated questions from unfamiliar sources.

Additionally, the Turing test, proposed by Alan Turing in 1950, is becoming less relevant as modern LLMs have advanced to the point where humans struggle to differentiate them from machines in text-based conversations. In robotics, new benchmarks like ARMBench focus on perception, while VIMA-Bench assesses simulated environments incorporating perception, communication, and deep learning.

### Natural Language Processing and MMLU
In NLP, state-of-the-art models like Gemini, Claude 3.5, and GPT-4o can reason across audio, images, and goal-oriented tasks. The Massive Multitask Language Understanding (MMLU) benchmark, created in 2020, tests performance across 57 subjects. OpenAI’s o1-preview achieved the highest recorded MMLU score of 92.3% in September 2024, compared to 86.4% for GPT-4 (March 2023) and 27.9% for RoBERTa in 2019—a 64.4 percentage point increase over five years. The human baseline is 89.8%. 

Due to MMLU's simplistic questions, MMLU-Pro was introduced in 2024 to remove trivialities and increase answer choices; DeepSeek-R1 currently holds the highest score on MMLU-Pro at 84.0%. To evaluate public preference, the LMSYS Chatbot Arena Leaderboard uses anonymous voting. As of early 2025, it has over 1 million votes, with a Google Gemini model as the most preferred. 

To reduce human curation costs, UC Berkeley researchers created BenchBuilder, an automated pipeline using LLMs to curate prompts. This was used to develop Arena-Hard-Auto, which uses 500 challenging queries with GPT-4 Turbo as the judge against a baseline (GPT-4-0314). As of November 2024, the top scores on Arena-Hard-Auto were o1-mini (92.0), o1-preview (90.4), and Claude-3.5-Sonnet (85.2). However, the November variant of Claude 3.5 Sonnet leads the style leaderboard.

### Significant Model and Dataset Releases of 2024
Throughout 2024, a high volume of notable AI releases occurred:
- **January 19:** Stable LM 2 (Stability AI) - 1.6B parameters, for portable devices.
- **February 8:** Aya Dataset (Cohere for AI, Beijing Academy of AI, Cohere, Binghamton University) - 513 million prompt-completion pairs in 114 languages.
- **February 15:** Gemini 1.5 Pro (Google DeepMind) - 1 million token context window, exceeding GPT-4 Turbo's 128K.
- **February 20:** SDXL-Lightning (ByteDance) - Fast text-to-image using progressive adversarial distillation.
- **February 25:** Claude 3 (Anthropic) - Outperforms GPT-4 and Gemini on benchmarks while reducing prompt refusals.
- **March 4:** Claude 3 (Anthropic) - (Note: Child context lists March 4 for Claude 3).
- **March 7:** Inflection-2.5 (Inflection AI) - GPT-4 level performance using 40% of GPT-4's compute; Microsoft acquired Inflection for $650 million two weeks later.
- **March 19:** Moirai and LOTSA (Salesforce) - Moirai is a foundation model for forecasting; LOTSA is a time series dataset with 27 billion observations in nine domains.
- **March 27:** DBRX (Databricks) - Open-source MoE transformer decoder-only model (132B parameters, 36B active), trained on 12 trillion tokens.
- **April 2:** Stable Audio 2 (Stability AI) - Song generator with audio-to-audio functionality.
- **April 17:** Llama 3 (Meta) - 8B and 70B parameter models.
- **May 13:** GPT-4o (OpenAI) - Multimodal model (text, audio, images, video) with audio responses in as little as 320 milliseconds.
- **June 7:** Qwen2 (Alibaba) - Base and instruction-tuned models rivaling Llama 3-70B and Mixtral-8x22B.
- **June 17:** Runway Gen-3 (Runway) - Text-to-video/image-to-video focusing on photorealistic humans.
- **July 23:** Llama 3.1 405B (Meta) - Most capable open-weight foundation model, rivaling closed models.
- **August 12:** Falcon Mamba (TII Abu Dhabi) - 7B parameter model using Mamba State Space Language Model (SSLM) architecture.
- **August 13:** Grok-2 (xAI) - Advanced reasoning and problem-solving model.
- **August 15:** Imagen 3 (Google Labs) - Highest Elo score on GenAI-Bench image benchmark.
- **August 22:** Jamba 1.5 (AI21 Labs) - Combines state-space models with transformers.
- **August 29:** SynthID v2 (Google) - Watermarking tool for AI-generated content.
- **September 11:** NotebookLM Podcast Tool (Google Labs) - End-to-end AI podcast generator.
- **September 12:** o1-preview (OpenAI) - First of 'o series' for advanced reasoning in math, science, and coding.
- **September 19:** Qwen2.5 (Alibaba) - Foundation models including specialized coding and math models.
- **September 17:** NVLM (D, H, X) (Nvidia) - Open-access vision-language models achieving top scores on VQAv2 and OCRBench.
- **October 16:** Ministral (Mistral) - 3B and 8B parameter models outperforming Gemma and Llama of similar size.
- **October 22:** Anthropic Computer Use (Anthropic) - Claude 3.5 Sonnet feature for autonomous cursor/typing in real time.
- **October 28:** Apple Intelligence (Apple) - Suite including Image Playground, Genmoji, and Siri integration with ChatGPT.
- **December 3:** Nova Pro (Amazon) - AWS Nova family, specializes in financial documents.
- **December 11:** Gemini 2 (Google DeepMind) - Twice as fast as Gemini 1.5 Pro, includes computer control and image/audio generation.
- **December 12:** Sora (OpenAI) - Video generation (1080p up to 20s for Pro, 720p up to 5s for ChatGPT Plus).
- **December 13:** Global MMLU (Cohere) - Multilingual MMLU translation in 42 languages.
- **December 20:** o3 (beta) (OpenAI) - Frontier model for PhD-level science, research math, and SWE, achieving 87.5% on ARC-AGI private holdout set.
- **December 27:** DeepSeek-V3 (DeepSeek) - Open-source model outperforming leading models on GPQA and MMLU.

### Final Technical Considerations
Despite these advances, complex reasoning remains a persistent problem. LLMs still struggle with logical reasoning, arithmetic, and planning, especially on instances larger than those they were trained on, limiting their reliability in high-risk applications. High-quality AI video generators, such as SORA, Veo 2, Google DeepMind, Movie Gen (Meta), and Stable Video 3D and 4D, showed significant improvement in 2024 over 2023 versions. 

Additionally, a new class of benchmarks like Humanity’s Last Exam (top score 8.80%), FrontierMath (solve only 2% of problems), and BigCodeBench (35.5% success rate vs. human 97%) have been introduced to replace saturated traditional benchmarks like MMLU, GSM8K, and HumanEval.

## Children
- [[content/L0/ai-technical-performance-2024-highlights|ai-technical-performance-2024-highlights]] — The Technical Performance chapter of the AI Index Report 2025 highlights that AI performance on MMMU and GPQA rose by 18.8 and 48.9 percentage points respectively, and that the gap between the top closed-weight and open-weight models on the Chatbot Arena Leaderboard narrowed from 8.04% to 1.70% between January 2024 and February 2025.
- [[content/L0/ai-2024-model-releases-performance|ai-2024-model-releases-performance]] — The 2024 AI timeline includes releases like OpenAI's o1 and o3, Meta's Llama 3.1 405B, and Google's Gemini 2, while AI performance on benchmarks like MATH (where AI now leads humans by 7.9 points) and MMMU (where o1 scored 78.2%) is rapidly approaching or exceeding human baselines.
- [[content/L0/open-vs-closed-weight-and-us-china-performance|open-vs-closed-weight-and-us-china-performance]] — The AI Index Report 2025 notes that the gap between open-weight and closed-weight models narrowed on MMLU from 15.9 points in 2023 to 0.1 in 2024, and the performance gap between US and Chinese models on MMLU fell from 17.5 points to 0.3 points over the same period.
- [[content/L0/ai-benchmarking-and-language-performance|ai-benchmarking-and-language-performance]] — The AI Index Report 2025 details the evolution of AI benchmarking, noting that OpenAI's o1-preview reached a record 92.3% on MMLU while the gap between the top and 10th ranked models on the Chatbot Arena narrowed to 5.4%. It also highlights benchmark deficiencies, such as the contamination of GSM8K and the creation of MMLU-Pro to provide a more rigorous evaluation of LLMs.
