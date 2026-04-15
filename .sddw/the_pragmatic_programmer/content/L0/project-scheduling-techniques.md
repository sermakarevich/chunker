# project-scheduling-techniques

**Parent:** [[content/L1/software-estimation-and-domain-modeling-principles|software-estimation-and-domain-modeling-principles]] — Software design requires prioritizing the domain's vocabulary (advanced practitioners may use internal languages like RSpec) over inherent programming language features (e.g., static vs. dynamic typing). Estimation involves establishing a model (through consulting experts or creating mental models) and decomposing it, ensuring the final answer is expressed in terms of critical, varying parameters, and all estimates require rigorous logging and must be communicated with the phrase, 'I’ll get back to you.'

To improve the accuracy of future estimates, individuals should maintain a log of their estimates, tracking how accurate the final results were. If an overall estimate requires calculating subestimates, the professional must also keep track of these subestimates. The goal is to observe the degree of accuracy in estimates. When an estimate proves incorrect, the professional should not disregard the failure; instead, the professional must investigate the root cause. Potential reasons for an error include choosing parameters that do not match the problem's reality or basing the estimate on an incorrect model. Uncovering the precise reason for the error will lead to better subsequent estimates. 

**ESTIMATING PROJECT SCHEDULES**

Project scheduling estimates typically involve determining the duration required for complex tasks, which can be challenging to predict. To manage this inherent uncertainty, two primary techniques are presented.

**Painting the Missile (Scenario-Based Estimation)**

In real-world scenarios, people often estimate duration not with a single number, but with a range of possibilities covering different scenarios. For example, estimating the time needed to paint a house might yield a low estimate (e.g., 10 hours, assuming ideal conditions and paint coverage), a more realistic estimate (e.g., 18 hours), and a pessimistic estimate (e.g., 30 hours or more, if the weather turns bad).

When the U.S. Navy planned the Polaris submarine project, they adopted this methodology, which they called the Program Evaluation Review Technique (PERT). Each PERT task requires three distinct estimates: an optimistic figure, a most likely figure, and a pessimistic figure. The professional arranges these tasks into a dependency network and uses simple statistics to calculate the likely best and worst possible times for the entire project. Using a range of values helps avoid a common source of estimation error: padding the number out of uncertainty. Instead, the statistics behind PERT distributes the uncertainty across the entire project, resulting in improved estimates for the whole scope.

**Eating the Elephant (Iterative Estimation)**

The most reliable way to determine a project's timetable is by gaining direct experience on the project itself. This necessity does not create a paradox if the professional practices incremental development by repeatedly completing the following steps with very small slices of functionality: checking requirements, analyzing risk (and prioritizing the riskiest items early), designing, implementing, integrating, and validating with the users. 

Initially, the professional may only have a general idea of how many iterations will be required or how long they may take. While some methods mandate nailing down this number during the initial planning phase, this practice is a mistake for all projects except the most trivial ones. Unless the project mimics a previous one with the same team and technology, guessing the timeline is unreliable. Therefore, the professional completes coding and testing of the initial functionality and marks this as the end of the first iteration. Based on this accrued experience, the professional can refine the initial guess regarding the number of iterations and the scope of work for each one. This refinement process improves with each cycle, and the confidence in the schedule grows accordingly. This method is often carried out during the team’s review at the conclusion of each iterative cycle, paralleling the principle of eating an elephant one bite at a time. The professional should formally refine the schedule as part of every iteration, helping management understand that the team's productivity, environment, and effort will determine the final schedule, providing the most accurate scheduling estimates possible. The best time to communicate the schedule is to tell stakeholders, “I’ll get back to you.”

For any estimate, the professional must allow adequate time to slow down and work through the descriptive steps provided in this section, as estimates given under pressure (like at a coffee machine) often prove inaccurate.

**RECOMMENDED ACTIONS:**
*   **Logging:** The professional should start keeping a detailed log of all estimates, tracking the accuracy of each prediction. If the error exceeds 50%, the professional must investigate the specific causes of the inaccuracy.
*   **Communication:** When asked for an estimate, the professional should respond, “I’ll get back to you.”
