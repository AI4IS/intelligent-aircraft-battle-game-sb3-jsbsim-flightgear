# Intelligent-aircraft-battle-game-sb3-jsbsim-flightgear
A simple template for intelligent air-to-air battle game using OpenAI stablebaselines3, jsbsim and flightgear. 

## For beginners
The whole project is designed with the following framework.
- Dynamic Model: JSBSim
- RL library: OpenAI Stablebaselines3
- Render: `.acmi` file (for tacview) or flightgear (simultaneously rendering while running)
- Trajectory drawing: `draw trajectory.ipynb`

This project only contains one type of aircraft, f16. If you want to add more kinds, please visit JSBSim official project and pick your favorate models.
NOTE: The maximum number of aircrafts that flightgear can render is two, if you want to render more, we suggest you using `.acmi` file.

## Advanced
If you want to reproduce our work, we recommend implementing the reinforcement learning algorithm in sb3 from scratch and using modular programming to facilitate parallel training and evaluation.

## Citing
If you find this project is useful, pleased use the following citation.
```
@demo{Wang2024github,
  author = {Dinghan Wang and Jiandong Zhang},
  title = {Intelligent aircraft battle game: using sb3, jsbsim and flightgear to achieve flexible realization and high fidelity},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/AI4IS/intelligent-aircraft-battle-game-sb3-jsbsim-flightgear}},
}
```
You can also refer to and cite our published articles.
```
@cja{Wang2024cja,
  author = {Jiandong Zhang^1, Dinghan Wang^1, Qiming Yang^*},
  title = {Loyal Wingman Task Execution for Future Aerial Combat: A Hierarchical Prior-based Reinforcement Learning Approach},
  year = {2024},
  publisher = {Elsevier},
  journal = {Chinese Journal of Aeronautics},
  howpublished = {\url{https://doi.org/10.1016/j.cja.2024.03.009}},
}
```

## Disclaimer
We love peace, and all of our offensive words such as air combat are limited to simulation games, so please do not misinterpret our work. We do not accept any accusation of militarization.
