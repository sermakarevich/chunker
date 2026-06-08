# ai-technical-performance-2025

**Parent:** [[index]]

The Technical Performance chapter of the Artificial Intelligence Index Report 2025, published by the AI Index Steering Committee at Stanford University's Institute for Human-Centered AI, provides an exhaustive analysis of AI benchmarks and model capabilities across language, vision, video, speech, and coding. The landscape in 2024-2025 is characterized by rapid mastery of benchmarks, performance convergence among frontier models, and a shrinking gap between open-weight and closed-weight models, as well as between US-based and Chinese models.

### Language and Reasoning Paradigms

AI systems are mastering new benchmarks at an unprecedented pace. For tests introduced in 2023 to push the limits of AI, performance gains by 2024 were remarkable: MMMU saw an increase of 18.8 percentage points, and GPQA saw a 48.9 percentage point increase. On SWE-bench, AI's ability to solve coding problems leaped from 4.4% in 2023 to 71.7% in 2024. In areas where humans still lead, the gap is closing; for instance, state-of-the-art AI systems are now 7.9 percentage points ahead of human performance on the MATH benchmark for competition-level mathematics, compared to a 0.3-point gap in 2024.

There is a clear trend of performance convergence at the frontier. The Elo score difference between the top-ranked and 10th-ranked models on the LMSYS Chatbot Arena Leaderboard narrowed from 11.9% to 5.4% by early 2025. The difference between the top two models shrank from 4.9% in 2023 to 0.7% in 2024. Current top providers include OpenAI, Google, Anthropic, Meta, Mistral AI, DeepSeek, and xAI.

New reasoning paradigms, specifically test-time compute and iterative reasoning, have improved performance. OpenAI's o1 and o3 models use these techniques, employing a chain-of-thought process to break complex problems into smaller steps and iteratively check answers. The o1 model scored 74.4% on an International Mathematical Olympiad (IMO) qualifying exam, whereas GPT-4o scored 9.3%. The o3 model achieved an 87.5% accuracy rate on the ARC-AGI benchmark, surpassing the previous record of 55.5%. However, these capabilities come with higher costs and latency. GPT-4o costs $2.50 per 1 million input tokens and $10 per 1 million output tokens, while o1 costs $15 per 1 million input tokens and $60 per 1 million output tokens. Additionally, o1 is approximately 40 times slower than GPT-4o, with a time to first token of 29.7 seconds compared to 0.72 seconds for GPT-4o.

Detailed benchmarks for language and reasoning include:
- **Arena-Hard-Auto:** Developed via the BenchBuilder automated pipeline to curate 500 challenging queries from the Chatbot Arena. As of November 2024, the top scores were o1-mini (92.0), o1-preview (90.4), and Claude-3.5-Sonnet (85.2). The November variant of Claude 3.5 Sonnet leads the style leaderboard.
- **WildBench:** Uses over 1 million human-chatbot interactions. GPT-4o is the top performer with an Elo score of 1227.1, followed by Claude 3.5 Sonnet (1215.4).
- **WildBench:** (Note: The children contexts provide duplicate information on WildBench).
- **MixEval-Hard:** OpenAI’s o1-preview achieved the highest score of 72.0, followed by Claude 3.5 Sonnet-0620 (68.1) and Llama-3.1-405B-Instruct (66.2).
- **MMM-U:** Consists of 11,500 college-level questions across six disciplines. OpenAI’s o1 scored 78.2%, improving upon the 59.4% state-of-the-art reported in the 2024 AI Index, but remaining below the human baseline of 82.6%.
- **GPQA:** A dataset of 448 expert-level multiple-choice questions in biology, physics, and chemistry. In 2023, GPT-4 scored 38.8% on the diamond test set; by December 2024, OpenAI's o3 achieved 87.7%, a 48.9 percentage point increase, exceeding the human baseline of 81.3%.
- **ARC-AGI:** Tests generalization beyond training. In 2020, the top score was 20%; by 2024, the top score rose to 33%. OpenAI's o3 achieved 75.7%, and with a high compute budget exceeding $10,000, reached 87.5%.
- **Humanity's Last Exam (HLE):** A benchmark of 2,700 multimodal questions. OpenAI's o1 scores 8.8%, Gemini 2.0 Flash Thinking (7.2%), Gemini 1.5 Pro (5.2%), Claude 3.5 Sonnet (4.8%), Grok-2 (3.9%), and GPT-4o (3.1%).

### Open-Weight vs. Closed-Weight Models and Global Competition

The gap between closed-weight and open-weight models has narrowed significantly. In early January 2024, the leading closed-weight model outperformed the top open-weight model by 8.04% on the Chatbot Arena, but by February 2025, this gap shrank to 1.70%. On the MMLU benchmark, closed-weight models led open models by 15.9 percentage points in late 2023, but this difference fell to 0.1 percentage point by the end of 2024. This shift was largely driven by Meta's Llama 3.1 and DeepSeek's V3.

Global competition between the US and China is also closing. In January 2024, the top US model outperformed the best Chinese model by 9.3% on the LMSYS Chatbot Arena, but by February 2025, the gap was 1.7%. Performance gaps on MMLU, MMMU, MATH, and HumanEval narrowed from 17.5, 13.5, 24.3, and 31.6 percentage points at the end of 2023 to 0.3, 8.1, 1.6, and 3.7 percentage points by the end of 2024. The launch of DeepSeek-R1 was particularly notable as it achieved these results using a fraction of the hardware resources typically required.

### Model Efficiency and Compact Models

Scaling has driven progress, but 2024 saw a breakthrough in smaller, high-performing models (Llama 3.1 8B, o1-mini, GPT-4o mini, Gemini 2.0 Flash, and Mistral Small 3.5). The MMLU benchmark exemplifies this: in 2022, the smallest model to score over 60% was PaLM (540 billion parameters); by 2024, Microsoft's Phi-3-mini achieved this with only 3.8 billion parameters, a 142-fold reduction in size.

### RAG, Embeddings, and Long-Context Retrieval

Retrieval-augmented generation (RAG) has evolved, with Anthropic introducing Contextual Retrieval in September 2024. New benchmarks for RAG include Ragnarok, CRAG, and FinanceBench.

Embedding models have seen progress. The Massive Text Embedding Benchmark (MTEB) evaluates models across 58 datasets and 112 languages. As of early 2025, Voyage AI’s voyage-3-m-exp (74.03) is the top-performing model, narrowly beating NV-Embed-v2 (72.31), with the leading score rising from 59.5 in late 2022.

Context windows have expanded from 2023 models like GPT-4 and Llama 2 (8,000 and 4,000 tokens, respectively) to modern models like GPT-4o and Gemini 2.0 Pro Experimental (128k to 2 million tokens). To evaluate these, Nvidia’s RULER benchmark assesses multihop reasoning and retrieval. Gemini-1.5-Pro achieved the highest weighted performance average of 95.5, followed by GPT-4 (89.0) and GLM4 (88.0). HELMET (How to Evaluate Long-Context Models Effectively and Thoroughly) found that Gemini 1.5 Pro and the August variant of GPT-4 maintained effectiveness, while GPT-4, Claude 3.5 Sonnet, and Llama 3.1-70B showed performance degradation.

### Computer Vision, Image and Video Generation

Computer vision benchmarks have moved from classification to reasoning. The Visual Commonsense Reasoning (VCR) challenge (2019) tests rationales for answers. In July 2024, a model reached a Q->AR score of 85.0, matching the human benchmark and improving 4.2% over 2023. For video understanding, the MVBench benchmark (2023) requires temporal reasoning. The top model is Video-CCAM-7B-v1.2 (based on Qwen 2.5-7B-Instruct) with a score of 69.23, a 14.6% improvement since late 2023.

Image generation has reached a point where human faces are often indistinguishable from real photos. In the Vision Arena, Google’s Gemini-2.0-Flash-Thinking-Exp-1219 is the top-ranked model, with only a 3.4% gap between it and the fourth-ranked ChatGPT-4o-latest (2024-1120).

Video generation saw a significant leap in 2024. Notable releases include Stability AI's Stable Video Diffusion (Nov 2023) and Stable Video 3D (Mar 2024). OpenAI's Sora (previewed Feb 2024, released Dec 2024) can generate 1080p 20-second videos for Pro users and 720p 5-second videos for ChatGPT Plus users. Meta's Movie Gen (Oct 2024) creates 16-second 1080p videos at 16 fps with sound and personalized video generation. Google's Veo and Veo 2 (Dec 2024) internally outperformed Movie Gen, Kling v1.5, and Sora Turbo. Other notable generators include Runway’s Gen-3 Alpha, Luma’s Dream Machine, and Kuaishou’s Kling 1.5.

### Speech and Coding

Speech recognition is evaluated on the LRS2 benchmark using Word Error Rate (WER). The model Whisper-Flamingo achieved a new standard with a WER of 1.3%.

Coding capabilities have risen dramatically. On the SWE-bench (October 2023), OpenAI’s o3 solved 71.7% of problems by early 2025, compared to 4.4% in late 2023. On BigCodeBench (2024), OpenAI’s o1 scored 35.5 on the hard subset. On the Chatbot Arena LLM coding filter, Gemini-Exp-1206 leads with a score of 1,369, followed by o1 at 1,361. Among Chinese models, DeepSeek-V3 leads with an Elo score of 1,317.

### Mathematics and Theorem Proving

Mathematical problem-solving spans from grade-school to competition level. On the GSM8K benchmark, a variant of Claude Sonnet 3.5 optimized using HPT prompting achieved 97.72%, increasing from the 2023 high of 91.00%. However, benchmarks like GSM8K may be approaching saturation.

For competition-level math, the MATH dataset (12,500 problems) is used. OpenAI’s o3-mini (high) achieved a record score of 97.9% in January 2025, surpassing the human baseline of 90%.

To address saturation, Epoch AI introduced FrontierMath. OpenAI’s o3 model scored 25.2%, while other models like o1-preview, o1-mini, GPT-4o, Claude 3.5 Sonnet, and Gemini 1.5 Pro (which initially solved only 2.0%) only solved a small fraction of problems.

In theorem proving, Google DeepMind’s AlphaProof and AlphaGeometry 2 (2024) solved four out of six problems in the 2024 International Mathematical Olympiad (IMO). AlphaProof uses a fine-tuned Gemini model and Lean formal proof system; AlphaGeometry 2 is a neuro-symbolic hybrid. Together, they achieved a performance level equivalent to an IMO silver medalist.

### Planning and Agentic Capabilities


AI agents are showing early promise. In 2024, VisualAgentBench (VAB) occurred. On the VAB test set, GPT-4o achieved the highest overall success rate at 36.2%, while most proprietary models averaged around 20%.

Planning is evaluated via PlanBench. In the Blocksworld zero-shot evaluation, OpenAI's o1 scored 97.8%, significantly outperforming Llama 3.1 405B (62.6%) and GPT-4o (35.5%). In the Mystery Blocksworld domain, o1 scored 52.8%, while Llama 3.1 405B scored 0.8% and Llama 3.1 405B scored 0.8% and GPT-4 scored 0%. However, o1 solves only 23.6% of planning instances that require 20 or more steps.

Research and development R&D agents are are evaluated via RE-Bench. In short time-horizon settings (two-hour budget), AI systems score four times higher than human experts. In a 32-hour budget setting, however, humans outperform AI by a factor of two. In specific tasks like writing Triton kernels, AI agents already match or exceed human expertise.

### Summary of Significant 2024 Releases

Throughout 2024, a high volume of notable AI releases occurred:
- **January 19:** Stable LM 2 (Stability AI) - 1.6B parameters.
- **February 8:** Aya Dataset (Cohere for AI, Beijing Academy of AI, uma Binghamton University) - 513 million prompt-completion pairs in 114 languages.
- **February 15:** Gemini 1.5 Pro (Google DeepMind) - 1 million token context window.
- **February 20:** SDXL-Lightning (ByteDance) - Fast text-to-image using progressive adversarial distillation.
- **February 25/March 4:** Claude 3 (Anthropic) - Reduced prompt refusals and outperforms GPT-4/Gemini.
- **March 7:** Inflection-2.5 (Inflection AI) - GPT-4 level performance using 40% of the compute.
- **March 19:** Moirai and LOTSA (Salfesforce) - Moirai is a forecasting model; LOTSA is a time series dataset with 27 billion observations.
- **March 27:** DBRX (Databricks) - Open-source MoE transformer decoder-only model (132B parameters, 36B active), trained on 12 trillion tokens.
- **April 2:** Stable Audio 2 (Stability AI) - Song generator with audio-to-audio functionality.
- **April 17:** Llama 3 (Meta) - 8B and 70B parameter models.
- **May 13:** GPT-4o (OpenAI) - Multimodal model with audio responses in as little as 320 milliseconds.
- **June 7:** Qwen2 (Alibaba) - Rivaling Llama 3-70B and Mixtral-8x22B.
- **June 17:** Runway Gen-3 (Runway) - Photorealistic humans in text-to-video/image-to-video.
- **June 17:** Runway Gen-3 (Runway) - (Duplicate in metadata).
- ** uma own August  uma own August 12:** Falcon Mamba (TII Abu Dhabi) - 7B parameter model using Mamba SSLM architecture.
- **August 13:** Grok-2 (xAI) - Advanced reasoning and problem-solving model.
- **August 15:** Imagen 3 (Google Labs) - Top Elo score on GenAI-Bench image benchmark.
- **August 22:** Jamba 1.5 (AI21 Labs) - Combines state-space models with transformers.
- **August 29:** SynthID v2 (Google) - Watermarking tool for AI-generated content.
- **September 11:** NotebookLM Podcast Tool (Google Labs) - end-to-end AI podcast generator.
- **September 12:** o1-preview (OpenAI) - Advanced reasoning for math, science, and coding.
- **September 19:** Qwen2.5 (Alibaba) - Specialized coding and math models.
- **September 17:** NVLM (Nvidia) - Open-access vision-language models.
- **October 16:** Ministral (Mistral) - 3B and 8B parameter models.
- **October 22:** Anthropic Computer Use (Anthropic) - Real-time autonomous cursor/typing for Claude 3.5 Sonnet.
- **October 28:** Apple Intelligence (Siri integration with ChatGPT, Image Playground, Genmoji).
- **December 3:** Nova Pro (Amazon) - Specializes in financial documents.
- **December 11:** Gemini 2 (Google DeepMind) - Twice as fast as Gemini 1.5 Pro.
- **December 12:** Sora (OpenAI) - 1080p 20-second videos for Pro, 720p 5-second videos for ChatGPT Plus.
- **December 13:** Global MMLU (Cohere) - Multilingual translation in 42 languages.
- **December 20:** o3 (beta) (OpenAI) - PhD-level science, research math, and SWE, 87.5% on ARC-AGI private holdout set.
- **December 27:** DeepSeek-V3 (DeepSeek) - Open-source model outperforming leading models on GPQA and MMLU.

### Final Technical Considerations

Despite these advances, complex reasoning remains a persistent problem. LLMs still struggle with logical reasoning, arithmetic, and planning, especially on instances larger than those they were trained on, which limits their reliability in high-risk applications. High-quality AI video generators, such uma same as and SORA, Veo 2, Movie Gen, Stable Video 3D and 4D, showed significant improvement in 2024 over 2023 versions.

To replace saturated traditional benchmarks like MMLU, GSM8K, and HumanEval, a new class of benchmarks have been introduced, including Humanity’s Last Exam (top score 8.80%), FrontierMath (solve only 2% of problems), and BigCodeBench (35.5% success rate vs. human 97%).


## Children
- [[content/L1/ai-technical-performance-benchmarks-2025|ai-technical-performance-benchmarks-2025]] — The AI Index Report 2025 highlights significant leaps in AI reasoning (OpenAI o1/o3), long-context retrieval (Gemini 1.5 Pro), and coding (o3 solving 71.7% of SWE-bench), while noting the saturation of early benchmarks like HumanEval.
- [[content/L1/ai-index-2025-technical-performance|ai-index-2025-technical-performance]] — The AI Index Report 2025 analyzes technical performance across coding, math, and reasoning, highlighting records such as OpenAI's o3 achieving 97.9% on the MATH dataset and 87.7% on the GPQA diamond set, while noting the saturation of benchmarks like GSM8K.
