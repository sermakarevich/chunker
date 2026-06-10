# ai-models-infrastructure-environmental-impact

**Parent:** [[content/L2/ai-index-report-2026-comprehensive|ai-index-report-2026-comprehensive]] — The 2026 AI Index Report details a 'jagged frontier' of AI capabilities, where the US and China trade the lead in model performance, and Grok 4's training emissions reached 72,816 tons of CO2e, while US private investment reached $285.9 billion in 2025.

The 2026 Artificial Intelligence Index Report provides a detailed technical analysis of the development of notable AI models, the infrastructure required to sustain them, and the environmental impacts resulting from their training and inference. 

### Notable AI Model Trends and Transparency

Frontier AI models are increasingly categorized by their access types and the transparency of their training processes. In 2025, there were 102 notable models. The distribution of access types was as follows: 47 models were available via API access, 19 via open weights (noncommercial), 14 via hosted access (no API), 13 via open weights (unrestricted), 13 via open weights (restricted use), 27 were unreleased, and 10 were unknown. Transparency regarding training code has declined significantly; of the 102 models, 81 had unreleased training code, 17 were unknown, 12 were open (restricted use), 9 were open (noncommercial), and only 4 were open source. 

Historically, parameter counts for notable AI models grew exponentially from the early 2010s through 2022. While reported growth has flattened since 2022, this is largely attributed to the fact that organizations like Google, Anthropic, and OpenAI no longer publicly disclose parameter counts, training dataset sizes, or training durations for their most resource-intensive models. 

### Training Compute, Data, and Scaling

Training compute requirements for notable models have risen by several orders of magnitude, with industry models dominating in scale. While U.S. models generally remain more computationally intensive than Chinese models, a lack of direct reporting from U.S. labs makes recent comparisons difficult. Key models tracked in training compute (measured in petaFLOP) include GPT-3 175B (davinci), ERNIE 3.0 Titan, GPT-4 (Mar 2023), Claude 3.5 Sonnet, Grok-2, Grok 4, DeepSeek-V3, Doubao-pro, Qwen2.5-72B, Qwen3-Max, and GLM-4.6.

As the industry approaches "peak data"—the point where high-quality human text and web data is exhausted—Epoch AI projects the depletion date to fall between 2026 and 2032. To combat this, researchers are exploring synthetic data. While synthetic data can accelerate training by 5 to 10 times through hybrid approaches, there is no definitive evidence it can fully replace real-world data in pre-training for general-purpose models. The SYNTHLLM family of models, trained entirely on synthetic data, performs well but still lags behind leading models. 

Conversely, data-centric methods focused on quality over quantity have shown significant gains. The Olmo 3.1 Think 32B model, despite having roughly 32 billion parameters (nearly 90 times fewer than Grok 4's 3 trillion parameters), achieved competitive results on the American Invitational Mathematics Examination (AIME) 2025. Specifically, AIME 2025 performance was: GPT-5 (high) at 94.3%, Gemini 1.5 Pro at 95.7%, Grok-4 at 92.7%, Claude Opus 4.5 at 91.3%, and OLMo 3 at 78.1%.

Synthetic data remains highly effective for post-training (fine-tuning and reinforcement learning), particularly for reasoning and long-context capabilities. However, the rise of AI-generated content is evident; Graphite research indicates that by January 2025, 51.72% of newly published online content was AI-generated, while human-generated content fell to 48.28%.

Due to the limitations of synthetic data, frontier labs are pivoting toward proprietary data. Examples include the May 2025 licensing agreement between the New York Times and Amazon, and similar strategic pursuits by Meta and health/life sciences firms like Bristol Myers Squibb.

### Infrastructure and Global Computing Capacity

AI development relies on an exponential increase in hardware performance. Between 2008 and 2025, peak computational performance grew across multiple precisions, specifically FP32, FP16, TF32 (19-bit), and Tensor-FP16/BF16. 

Hardware adoption for notable models is centered on specific accelerators. By 2025, 84 notable models were trained on A100-class hardware, 69 on V100, 44 on TPU v3, 28 on TPU v4, 28 on H100, 4 on H800, and 6 on P100, with another 54 models using other accelerators.

Global AI computing capacity has increased by 3.3x per year since 2022, reaching approximately 17.1 million H100-equivalents by 2025. Nvidia is the dominant provider, accounting for 17.07M H100e, while Google, Amazon, AMD, and Huawei each contribute approximately 1.88M H100e. 

### Data Center Distribution and Power

AI data center infrastructure is highly centralized. The supply chain depends on high-bandwidth memory (HBM) from SK Hynix, Samsung, and Micron, and fiber-optic connectivity via InfiniBand. Fabrication is almost entirely dependent on TSMC in Taiwan, which produces virtually every leading chip, including Nvidia's Blackwell GPUs and AMD's MI300X.

In 2025, the United States led in data center count with 5,427 facilities, followed by Germany (529), the United Kingdom (523), China (449), Canada (337), France (322), Australia (314), Netherlands (298), Russia (251), Japan (222), Brazil (197), Mexico (173), Italy (168), India (153), and Poland (144).

By Q4 2025, total AI data center power capacity reached 29.56 GW. This is compared to the peak demand of New York state (approximately 31 GW), the Netherlands (approximately 20 GW), and New Zealand (approximately 7 GW). Of this total, 11.82 GW was attributed to AI chip power (TDP), while 17.74 GW was for supporting infrastructure (cooling, networking).

### Environmental Impact: Energy, Carbon, and Water

While hardware has become approximately 10 times more efficient per watt over the last decade, the scaling of models has outpaced these gains. Total power draw for frontier models has increased by several orders of magnitude; Grok 3 and Llama 4 Behemoth (preview) now require upward of 100 million watts.

Carbon emissions from training have surged. Training AlexNet in 2012 produced 0.01 tons of CO2 equivalent, while training Grok 4 in 2025 produced 72,816 tons—far exceeding the lifetime emissions of an average car (63 tons). Other model emissions include Llama 3.1 405B (8,930 tons), GPT-4 (5,184 tons), Megatron-Turing NLG (1,432 tons), and GPT-3 (588 tons).

Inference energy and carbon footprints are also significant. For medium-length prompts (1,000 input/output tokens), DeepSeek V3.2 Exp and V3.2 consumed the most energy (23.24 Wh and 23.13 Wh, respectively) and produced the highest carbon emissions (13.95 gCO2e and 13.88 gCO2e). In contrast, Claude 4 Opus consumed 5.32 Wh and produced 1.6 gCO2e, while Mistral Medium 3 produced the lowest emissions at 1.52 gCO2e. 

At a per-query level, a short GPT-4o query consumes 0.42 Wh (40% more than a Google search at 0.3 Wh). A daily session of eight medium-length queries costs 9.71 Wh, which is comparable to charging two smartphones (10 Wh).

Water consumption for GPT-4o inference is estimated between 1,334,991 and 1,579,680 kiloliters annually, exceeding the drinking water needs of 1.2 million people (1,314,000 kL).

### AI Infrastructure Power Demand

Cumulative power demand for AI accelerator modules through 2024 reached approximately 5,200 MW, with the total all-in AI system demand (including servers and cooling) reaching 9,400 MW. This is comparable to the national electricity consumption of Switzerland (15,000 MW) or Austria (15,000 MW), and roughly half that of Bitcoin mining (25,000 MW). Total global data center demand (excluding crypto) is estimated at 47,000 MW.

Regional electricity consumption for data centers has increased across all major regions, with the United States holding the largest share, followed by China, Europe, and the rest of Asia.

### Open-Source AI Software Development

AI-related GitHub projects grew from 1,549 in 2011 to 5.58 million in 2025. However, most are experimental; only 206,880 projects have at least 10 stars. Among these significant projects, the United States' share declined from nearly 80% in 2011 to 31.71% in 2025. Europe (24.47%), the rest of the world (27.63%), and China (11.01%) have grown, while India accounts for 5.2% of the projects. Despite this distribution, the U.S. remains the most engaged, with cumulative GitHub stars for AI projects totaling 30 million.

## Children
- [[content/L0/notable-ai-model-trends-compute-data|notable-ai-model-trends-compute-data]] — The 2026 AI Index Report highlights a shift from indiscriminate data scaling to data-centric methods, noting that high-quality human data may be depleted by 2026-2032 and AI-generated content reached 51.72% of new online content by January 2025. While parameter growth appears to flatten after 2022, this is likely due to missing data from major labs, and the Olmo 3.1 Think 32B model achieves competitive performance on AIME 2025 (78.1%) despite having 90x fewer parameters than Grok 4.
- [[content/L0/ai-infrastructure-compute-energy-environmental-impact|ai-infrastructure-compute-energy-environmental-impact]] — The 2026 AI Index Report indicates that global AI compute capacity grew 3.3x per year since 2022 to 17.1 million H100-equivalents, while the US hosts 5,427 data centers. Training emissions for Grok 4 in 2025 reached 72,816 tons of CO2 equivalent, vastly exceeding the lifetime emissions of an average car (63 tons).
- [[content/L0/ai-inference-environmental-impact-open-source|ai-inference-environmental-impact-open-source]] — The 2026 AI Index Report details that DeepSeek V3.2 Exp and V3.2 consume the most energy per query (23 Wh) and produce the most carbon emissions (14 gCO2e), while GPT-4o's annual water use for inference is estimated between 1.3 and 1.6 million kiloliters. Additionally, it notes a growth in open-source AI projects on GitHub, reaching 5.6 million projects by 2025, with the US maintaining the highest cumulative engagement (30 million stars).
