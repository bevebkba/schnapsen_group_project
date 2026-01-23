# is_group_project
**Search Depth Drives Stability**

## Project Overview
This project investigates whether increasing search depth in Schnapsen-playing bots
reduces the variance of game outcomes while improving performance stability.

The central research question is:

> Does increasing search depth reduce the variance of game outcomes?

The study compares simple rule-based bots with different fixed search depths,
ranging from no lookahead to shallow lookahead, against a static opponent.

---

## Experimental Setup
All experiments are conducted in a controlled environment:
- Game rules and implementation remain unchanged
- A fixed random opponent is used in all matches
- Only one variable (search depth) is modified per experiment

This setup ensures that observed differences are attributable solely to search depth.

---

## Variables
### Independent Variable
- Search depth of the evaluated bot:
  - Depth 0: No lookahead (random move selection)
  - Depth 1: One-step lookahead
  - Depth 2 (optional): Two-step lookahead
  - (We are planning to add more independed variables like samples)

### Dependent Variables
- Win rate
- Outcome variance (stability of performance)

---

## Bot Configuration
- **Evaluated Bot:** Simple rule-based bot with variable search depth
- **Opponent Bot:** Static random bot (no learning, no adaptation)

---

## Experimental Procedure
For each search depth:
1. The evaluated bot plays a fixed number of games
2. Each game is played under identical conditions
3. Results are recorded (win/loss, final score)
4. Win rate and outcome variance are computed

---

## Expected Outcome
- Increasing search depth is expected to:
  - Reduce outcome variance (more consistent performance)
  - Potentially increase win rate due to better decision-making

---

## Setup Instructions (for Group Members)
```bash
git clone https://github.com/bevebkba/is_group_project.git
cd is_group_project
conda env create -f environment.yml
conda activate is_group_project