# estimating-project-schedules

**Parent:** [[content/L1/estimation-productivity-and-data-standards|estimation-productivity-and-data-standards]] — Developers must master estimation techniques like using PERT (optimistic, most likely, pessimistic time) and practicing iterative development (Eating the Elephant Technique) by focusing on refining schedules based on recorded experience. Technical proficiency requires using plain text for self-describing data (over binary formats), utilizing the command shell as the primary workspace (through aliases and functions), and always anticipating the need to operate beyond the limitations of IDEs or GUIs.

When an estimate proves inaccurate, the primary action should be to determine the root cause of the discrepancy. Potential causes include selecting parameters that do not reflect the reality of the problem or relying on a flawed underlying model. Regardless of the specific reason, taking time to investigate what happened will improve the accuracy of future estimations.

### ESTIMATING PROJECT SCHEDULES

Developers are frequently asked to estimate the time required for a task. If the task is complex, generating an estimate can be difficult. This section details two techniques for mitigating that inherent uncertainty.

**Painting the Missile Technique:**
When estimating project timelines in the real world, people rarely provide a single number. Instead, they typically estimate using a range of scenarios. For example, estimating how long it will take to paint a house: a positive scenario might suggest a minimum of 10 hours, a more realistic figure might be closer to 18 hours, and a negative scenario (such as bad weather) could push the required time to 30 hours or more.

Historically, when the U.S. Navy needed to plan the Polaris submarine project, the team adopted this range-based estimation style using a methodology called the Program Evaluation Review Technique (PERT). Every task utilizing PERT involves three estimates: an optimistic time, a most likely time, and a pessimistic time. The tasks must be organized into a dependency network, and simple statistics are used to identify the likely best and worst times for the overall project. Using a range of values, such as those provided by PERT, helps avoid a common source of estimation error: padding a number out of uncertainty. Instead, the statistics within PERT distribute the overall project uncertainty, yielding better estimates for the whole project.

*Caveat:* Despite the quantitative nature of PERT, people tend to create large, wall-sized charts of all project tasks and implicitly believe that simply using a mathematical formula grants accuracy. However, this is often not the case, as individuals rarely have prior experience with the technique.

**Eating the Elephant Technique:**
Determining a project's timeline often requires practical experience gained during the project itself. This need does not constitute a paradox if the developer practices incremental development by repeatedly completing the following steps using very thin slices of functionality:
1. Analyze requirements.
2. Analyze risks (and prioritize the riskiest items earlier).
3. Design, implement, and integrate the functionality.
4. Validate the functionality with the users.

Initially, a developer may have only a vague idea of how many iterations or how long these iterations will take. While some methods require nailing down the number of iterations in the initial plan, this is a mistake for all projects except the most trivial ones. If a team is not working on an application similar to a previously completed one, using the same team and the same technology, initial estimates are mere guesses. The developer should complete the coding and testing of the initial functionality and mark this as the end of the first iteration. Based on that recorded experience, the team can refine the initial guess regarding the number of required iterations and the scope of work included in each. This refinement improves with each cycle, and the team's confidence in the schedule grows. This type of iterative estimation is typically conducted during the team’s review at the end of each iterative cycle. This process is analogous to the old idiom of eating an elephant: taking the endeavor one bite at a time.

**Tip for Scheduling:**
Management may typically desire a single, definitive number for the project schedule before work begins. However, the team should help management understand that the final schedule depends on the team's overall productivity and the working environment. By formalizing the process and refining the schedule as part of every iteration, the developer will provide the most accurate scheduling estimate possible.

**Best Practice:**
When questioned about an estimate, a developer should always respond with, “I will get back to you.” Delaying the response and spending time going through the structured steps described here generally yields better results than providing a quick estimate (like those given at a coffee machine).
