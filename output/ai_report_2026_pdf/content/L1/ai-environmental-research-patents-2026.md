# ai-environmental-research-patents-2026

**Parent:** [[content/L2/ai-index-report-2026-comprehensive|ai-index-report-2026-comprehensive]] — The 2026 AI Index Report details a 'jagged frontier' of AI capabilities, where the US and China trade the lead in model performance, and Grok 4's training emissions reached 72,816 tons of CO2e, while US private investment reached $285.9 billion in 2025.

The 2026 Artificial Intelligence Index Report provides a comprehensive analysis of the global AI ecosystem, spanning environmental impacts, software development, academic research, and commercial innovation through patents. 

### Environmental and Infrastructural Impacts

While training costs often dominate discussions, inference represents a growing share of AI's energy footprint. Once deployed at scale, the cumulative energy required to serve queries can exceed training costs within months. According to benchmarking by Jegham et al. (2025), energy consumption and carbon emissions for medium-length prompts (approx. 1,000 input and 1,000 output tokens) vary wildly by model. In 2025, DeepSeek V3.2 Exp and DeepSeek V3.2 consumed the most energy at 23.24 Wh and 23.13 Wh per query, respectively, followed by GPT-5 (high) at 21.85 Wh and o3-pro at 21.77 Wh. Lower consumption models include GPT-5 mini (medium) at 5.13 Wh and Claude 4 Opus at 5.32 Wh. 

Carbon emissions mirror this energy trend. DeepSeek V3.2 Exp (13.95 gCO2e) and DeepSeek V3.2 (13.88 gCO2e) produced the highest emissions per medium-length prompt, while Mistral Medium 3 (1.52 gCO2e) and Claude 4 Opus (1.60 gCO2e) produced the lowest. 

At the per-query level, a short GPT-4o query consumes 0.42 Wh, which is 40% more than a Google search (0.3 Wh). A daily session of eight medium-length queries requires 9.71 Wh, which is comparable to charging two smartphones (10.00 Wh). Water consumption for GPT-4o inference is also substantial, with annual estimates between 1,334,991 and 1,579,680 kiloliters; the higher end of this range exceeds the annual drinking water needs of 1.2 million people (1,314,000 kL).

From an infrastructure perspective, cumulative power demand from AI accelerator modules through 2024 reached approximately 5,200 MW, with Nvidia holding the largest share. Total demand, including servers, cooling, and networking, reached approximately 9,400 MW. This total is comparable to the national electricity consumption of Switzerland or Austria and roughly half that of Bitcoin mining (approx. 20,000 MW vs 47,000 MW for total global data centers excluding crypto). 

GPU computation costs have fallen by over 99% since 2006 (index value of 0.002 in 2024), enabling the scaling of models. Regional electricity consumption for data centers is projected to rise through 2030, with the United States holding the largest share, followed by China, Europe, and the rest of Asia.

### Open-Source AI Software Development

AI-related GitHub projects grew from 1,549 in 2011 to 5.58 million in 2025, with a 23.7% year-over-year growth from 2024. However, most are experimental; only 206,880 projects in 2025 had 10 or more stars. The geographic distribution of these visible projects has shifted: the U.S. share fell from nearly 80% in 2011 to 31.71% in 2025, while Europe (24.47%), the Rest of the World (27.63%), China (11.01%), and India (5.18%) grew. Total stars for AI projects increased from 14 million in 2023 to 18.2 million in 2025. Cumulatively, the U.S. remains the most engaged, with 30.02 million cumulative stars, followed by the Rest of the World (15.27 million), Europe (12.99 million), China (9.00 million), and India (2.50 million).

Complementing GitHub, Hugging Face provides a repository for models and datasets. Between 2022 and 2025, model uploads rose from 3,000 (2022Q1) to 332,000 (2025Q4), and dataset uploads rose from 3,000 to 153,000. Analysis of the top 200 most-downloaded models per week (representing 49.6% of normalized downloads) shows a shift in download share. As of 2025Q3, the U.S. holds a 17% share, followed by unaffiliated users (14%), International/Online (12%), China (12%), and the UK (11%). Major private developers like Google and Meta now account for a smaller share of downloads compared to community-led projects. 

Modality trends on Hugging Face have shifted dramatically. In 2022, text embedders, classifiers, and audio models accounted for nearly 70% of downloads (Text embed/class: 57.46%, Audio: 10.82%). By 2025, these fell to less than 6% (Text embed/class: 2.71%, Audio: 2.88%). Instead, text generation (42.46%), image generation (25.61%), and multimodal generation (13.30%) have become dominant.

### Academic Research and Publications

AI publications in computer science (CS) more than doubled between 2013 and 2024, from roughly 102,000 to 257.89 thousand, representing 40.9% of all CS publications in OpenAlex. In 2024, journals were the primary venue (47%), followed by conferences (23.5%). Total attendance at 16 major AI conferences in 2025 reached 101.12 thousand, with NeurIPS (26.38k), ICLR (11.04k), and CVPR (9.38k) being the largest. 

Geographically, China produced 17.76% of AI publications in 2024, followed by the Rest of the World (17.10%), Europe (11.05%), India (7.55%), and the United States (7.29%), though 39.25% of publications had an unknown country affiliation. In terms of citations, China led with 20.6%, followed by Europe (19.5%) and the U.S. (12.6%). 

Sectorally, academia produced 68.13% of 2024 publications, followed by government (12.44%) and industry (11.47%). In the U.S., industry's share was higher (24.46%) than in China (17.96%), while China's government sector was more significant (25.10%). Europe had the highest academic share at 55.3%. 

Research remains concentrated in machine learning (37%), computer vision (22.4%), pattern recognition (11.2%), and natural language processing (10%). The most-cited publications from 2021-2024 show a shift: the U.S. share of the top 100 publications declined from 64 (2021) to 46 (2024), while China's rose from 33 (2021) to 41 (2024) and Australia's rose from 2 (2021) to 14 (2024). In 2024, Google and Stanford University led with 7 top-cited publications each, followed by the Chinese Academy of Sciences and Microsoft (5 each).

### Global AI Patent Trends

Granted AI patents grew exponentially from 3,866 in 2010 to 131,121 in 2024. China dominates this landscape, accounting for 74.24% of global patents (97.99 thousand), followed by the U.S. (12.06%, 15.92 thousand), and the Rest of the World (10.35%, 13.66 thousand). In 2024, South Korea had the highest per capita patent rate (14.31 per 100,000 inhabitants), followed by Luxembourg (12.25) and China (6.95).

Despite China's volume, the U.S. maintains high downstream influence, accounting for 51.91% of forward citations (compared to China's 29.81%). U.S. patents are also cited more quickly; only 19% of U.S. patents remain uncited after 10 years, compared to 44% for Chinese patents. 

Technological proximity analysis shows most countries align with both the U.S. and China, though Denmark is an outlier with only 52% overlap with the U.S. and 45% with China, due to its focus on energy and wind-related technology (codes Y02E, F03D, F05B). 

Example patents include Chinese patent CN111431996A (resource configuration using ML), U.S. patent US11436777B1 (hazard visualization), and U.S. patent US202323945 la (VR/AR stereoscopic view synthesis).

## Children
- [[content/L0/open-source-ai-software-engagement|open-source-ai-software-engagement]] — U.S.-based AI projects on GitHub accumulated 30.02 million stars by 2025, while on Hugging Face, model uploads tripled and dataset uploads grew fourfold from 2023 to 2025, with text generation modalities leading with 42.46% of downloads by 2025.
- [[content/L0/ai-publications-and-citations-analysis|ai-publications-and-citations-analysis]] — AI publications more than doubled between 2013 and 2024, reaching approximately 258,000, with academia producing 68.1% of them in 2024. China leads in publication volume (17.8%) and citation share (20.6%) in 2024, while the US share of the top 100 most-cited publications declined from 64 in 2021 to 46 in 2024.
- [[content/L0/ai-research-patents-impact-analysis|ai-research-patents-impact-analysis]] — This section details a shift in AI research impact, with the US leading in forward citations (51.91%) and citing speed, but China dominating in patent volume (74.24% of global total) and overall publication count.
