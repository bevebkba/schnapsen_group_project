# The Impact of Search Depth on R-deep Schnapsen Agents
**Analyzing Win-Rate Variance in Imperfect-Information Game AI**

## Project Overview
This project investigates the impact of search depth on the performance stability of R-deep Monte Carlo Schnapsen agents. The primary focus is on analyzing the variance in win rates rather than just the average win rate. Evaluations are conducted against multiple opponent strengths categorized as easy, medium, and hard to provide a comprehensive assessment of agent behavior across varying competitive levels.

---

## Experimental Setup
We conducted large-scale tournaments where the R-deep agent's search depth was systematically increased from 1 up to 1000. Matches alternated the starting player to mitigate first-move advantages. The R-deep agent was evaluated against multiple opponents, including BullyBot, Bully+AlphaBeta, and R-deep+AlphaBeta agents, to assess performance across different strategic complexities.

---

## Variables
### Independent Variable
- Search depth of the R-deep agent (ranging from 1 to 1000)

### Dependent Variables
- Win rate
- Win-rate variance

---

## Bot Configuration
- **Evaluated Bot:** R-deep agent with fixed sample size and varying search depth
- **Opponent Bots:**
  - Easy: BullyBot (simple heuristic-based agent)
  - Medium: Bully+AlphaBeta (heuristic agent enhanced with AlphaBeta pruning)
  - Hard: R-deep+AlphaBeta (advanced agent combining R-deep Monte Carlo with AlphaBeta search)

---

## Experimental Procedure
For each search depth:
1. The R-deep agent plays a large number of games against each opponent type
2. Starting player alternates between games
3. Results are recorded (win/loss, final score)
4. Win rate and win-rate variance are computed

---

## Key Findings
- Performance changes rapidly at shallow search depths, indicating significant strategic improvements early on
- No consistent monotonic reduction in win-rate variance is observed at higher search depths, suggesting diminishing returns in stability
- Computational cost increases substantially with larger search depths, highlighting a trade-off between performance and resource usage

---

## Repository Structure
- `easy_tournament.py`: Scripts for running tournaments against the easy opponent (BullyBot)
- `normal_tournament.py`: Scripts for medium difficulty tournaments against Bully+AlphaBeta
- `hard_tournament.py`: Scripts for hard difficulty tournaments against R-deep+AlphaBeta
- CSV result files: Contain detailed game outcomes and statistics used for analysis
- Appendix: Includes extended results and methodological details referenced in the submitted paper

---

## Setup Instructions (for Group Members)
```bash
git clone https://github.com/bevebkba/schnapsen_group_project.git
cd schnapsen_group_project
conda env create -f environment.yml
conda activate is_group_project
```