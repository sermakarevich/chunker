# version-control-best-practices

**Parent:** [[content/L1/developer-productivity-and-workflow|developer-productivity-and-workflow]] — Software development requires mastery of editor fluency for text manipulation, utilizing VCS for comprehensive project management, and employing systematic debugging techniques like 'chop' and tracing statements to identify bugs efficiently.

Version control systems (VCS) are essential for managing software development, offering far more than a simple 'undo' function. While a personal computer's undo key helps recover from recent mistakes, a VCS acts as a comprehensive, project-wide time machine capable of restoring code to previous states, even if the mistake happened weeks earlier. VCS usage should not be limited only to managing source code; every type of digital artifact—including documentation, phone number lists, memos to vendors, makefiles, build and release procedures, and small shell scripts—must be placed under version control. The process is necessary even for individual-person teams on one-week projects or for 'throw-away' prototypes.

Sharing project source files across a network or using cloud storage for collaboration is not viable, as this practice frequently leads to teams messing up each other’s work, losing changes, breaking builds, and causing interpersonal conflicts. Similarly, keeping the main repository on a network or cloud drive is worse, as the version control software uses interacting files and directories; if two instances simultaneously make changes, the overall state can become corrupted, potentially causing irreparable damage.

From a technical perspective, VCS systems track every change made to source code and documentation. Using a properly configured source code control system allows users to always revert to previous software versions. Beyond simple mistake reversal, a VCS provides invaluable data for bug tracking, auditing, performance analysis, and quality control. Specific information users can track includes: who made changes in a particular line of code; the difference between the current version and a previous week's version; the total number of lines of code changed in a release; and which files are changed most often. Furthermore, VCS can identify and regenerate specific software releases, independent of any subsequent changes.

In addition to centralizing the files in a repository (which is a suitable candidate for archiving), VCS allows two or more users to work concurrently on the same set of files, even making simultaneous changes to the same file. The system then manages the process of merging these changes when the files are returned to the repository, a practice that, although seeming risky, works effectively on projects of all sizes.

The most powerful feature of VCS is the ability to use **branching**. Users can create a branch at any point in the project's history, and all work done in that branch remains isolated from all other branches. Eventually, the user can merge the changes from the working branch back into the target branch, incorporating the changes. Multiple people can even work on a separate branch, functioning essentially as little clone projects. This isolation benefits teams, allowing one developer to develop Feature A in one branch while a teammate works on Feature B in another, preventing interference.

Additionally, branches are often central to a team’s project workflow. Although many sources provide conflicting advice on implementation, users should search for viable solutions and remember to review and adjust their approach as they gain experience.

**Version Control as a Project Hub:**
While VCS is highly valuable for personal projects, its true utility emerges when used in a team environment. Although many VCS are decentralized, allowing developers to cooperate on a peer-to-peer basis, establishing a central repository is highly recommended. This central hosting allows a team to take advantage of numerous integrations that streamline project flow. Recommended features for a central repository include:
*   Good security and access control.
*   An intuitive User Interface (UI).
*   The ability to operate everything from the command line for automation.
*   Automated builds and tests.
*   Robust support for branch merging (also called pull requests).
*   Integrated issue management (allowing metrics tracking in commits and merges).
*   Good reporting (such as a Kanban board-like display of pending issues and tasks).
*   Effective team communications (e.g., email or other notifications upon changes, and a wiki).

Many teams configure their VCS so that a push to a particular branch automatically initiates the system build, runs tests, and, if successful, deploys the new code into production. Because version control allows recovery, the resulting process is reliable.

**Practical Challenges:**
Users should proactively learn the commands necessary to recover their own laptop environment in case of a disaster. The recovery process requires storing more than just text files, including system configuration and installed applications, by expressing all necessary components in text files and ensuring these files are hosted in a VCS separate from the laptop itself. Users should also consciously explore and implement advanced features like feature branches, pull/merge requests, continuous integration (CI), continuous build pipelines, and continuous deployment (CD), and review team communication tools like wikis and Kanban boards, even if not all are used, to make informed decisions about required tools.
