# software-entropy-and-broken-windows

**Parent:** [[content/L1/pragmatic-programmer-philosophy-and-accountability|pragmatic-programmer-philosophy-and-accountability]] — Pragmatic programming requires developers to take full ownership of their careers and projects, emphasizing continuous improvement (Kaizen), managing technical entropy, and maintaining transparency in failures by admitting errors immediately and providing solutions.

## Topic 3: Software Entropy

While software development is immune from almost all physical laws, the inexorable increase in entropy, a term from physics referring to the amount of "disorder" in a system, hits software projects hard. The laws of thermodynamics guarantee that the entropy in the universe tends toward a maximum. When disorder increases in software, developers call it "software rot." Some people might call this phenomenon the more optimistic "technical debt," implying the notion that the team will pay it back someday, but these promised repayments rarely materialize.

Regardless of whether the name is debt or rot, both forms of disorder can spread uncontrollably. Numerous factors contribute to software rot, yet the most important factor appears to be the project's underlying psychology, or culture. Even when the team consists of only one person, the project’s psychology can be very delicate. Despite the best-laid plans and the best personnel, a project can still experience ruin and decay during its lifespan. Conversely, some projects successfully fight nature’s tendency toward disorder, even when facing enormous difficulties and constant setbacks, and manage to achieve positive outcomes.

Researchers in the field of crime and urban decay discovered a fascinating trigger mechanism explaining why some buildings in inner cities are beautiful and clean, while others are rotting hulks. This mechanism involves a broken window: one broken window, left unrepaired for any substantial length of time, instills in the building's inhabitants a sense of abandonment, suggesting that the governing powers do not care about the structure. This sense of abandonment then causes subsequent problems, such as the breaking of another window, people starting to litter, and graffiti appearing, eventually leading to serious structural damage. In a relatively short span of time, the building becomes damaged beyond the owner’s desire to fix it, and the sense of abandonment becomes reality.

This psychological effect is impactful because psychologists have conducted studies showing that hopelessness can be contagious. Ignoring a clearly broken situation reinforces the idea that nothing can be fixed, that no one cares, and that everything is doomed; these negative thoughts can spread among team members, creating a vicious spiral.

**Tip 5: Don’t Live with Broken Windows**

Developers must not leave "broken windows"—which include bad designs, wrong decisions, or poor code—unrepaired. Instead, fix each issue as soon as it is discovered. If insufficient time exists to fix the issue properly, developers should board it up. Possible actions include commenting out the offending code, displaying a "Not Implemented" message, or substituting dummy data instead. Taking any action prevents further damage and demonstrates that the team is fully aware of the situation.

Clean, functional systems deteriorate rapidly once the first window breaks. Although other factors contribute to software rot, neglect accelerates the rot faster than any other factor. If a team lacks the time to clean up all the broken glass of a project, the team should plan on obtaining a dumpster or relocating to a different neighborhood. Teams must not let entropy win.

**FIRST, DO NO HARM**

During one instance, Andy’s acquaintance, who was obscenely rich, had an immaculate house loaded with priceless antiques and objets d’art. A fire started when a tapestry hung too close to a fireplace caught fire. Although the fire department rushed in to save the day and the house, before deploying big, dirty hoses, the department personnel paused to roll out a mat between the front door and the source of the fire. This demonstrated that the personnel did not want to mess up the carpet. This behavior illustrates that even when the fire department's first priority is putting out the fire, the personnel assessed the situation and were careful not to inflict unnecessary damage to the property. This caution must apply to software: developers must not cause collateral damage simply because of a crisis. One broken window—a badly designed piece of code, or a poor management decision that the team must live with for the project's duration—is enough to start the decline. If a development team finds itself working on a project with quite a few broken windows, it is easy to slip into the mindset that "All the rest of this code is crap, I’ll just follow suit." This outcome mirrors an original experiment where an abandoned car sat untouched for a week, but once a single window was broken, the car was stripped and turned upside down within hours.

By the same token, if a development team finds itself working on a project where the code is pristinely beautiful—cleanly written, well designed, and elegant—the team will likely take extra special care not to mess up the code, similar to the careful firefighters. Even if a fire is raging (such as a deadline, release date, or trade show demo), the team must not be the first one to make a mess and inflict additional damage.

Developers must remind themselves: “No broken windows.”

RELATED SECTIONS INCLUDE:
*   Topic 10, Orthogonality
