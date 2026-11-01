# 19 รถเลือกเลข (Car Number Choice)

A gate-choosing racing game. Pick the right gate in each sub-stage to manage your car's speed, then clear the final ramp.

## Team

| Name | Student ID | GitHub |
|------|-----------|--------|
| Pusit Pattamasarawut | 6934453923 | [@Pusit-P](https://github.com/Pusit-P) |
| _<Member B>_ | _<ID>_ | _<@username>_ |
| Nature Tavesat | 6934437923 | [@naturetavesat](https://github.com/naturetavesat) |

## Game Rules

- Start with a random speed. Speed acts as your health points.
- Each run has 5 to 10 sub-stages, and each has 2 gates (A and B). Pick one.
- Gates change speed: `+`, `-`, `x`, `/` (division rounds down).
- At the end, a ramp requires a minimum speed. If your speed is lower, you lose.

## Features

- Main menu (Play, Settings, Player) and car selection
- Mouse or keyboard controls
- Gates and ramp
- _Additional: tutorial, difficulty, sound, Mystery Door, shop, Thai/English_

## How to Run

Requires Python 3.10+.

```bash
git clone https://github.com/naturetavesat/car-number-choice.git
cd car-number-choice
pip install -r requirements.txt
python main.py
```
