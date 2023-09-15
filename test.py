from ranked_system_evaluator import (
    RankedSystemEvaluator,
    RankedSystem,
    Matchmaker,
    EloUpdater,
    GameSimulator,
)


if __name__ == "__main__":
    evaluation = RankedSystemEvaluator(
        ranked_system=RankedSystem(
            matchmaker=Matchmaker(
                game_team_count=20,
                game_time_size=3
            ),
            elo_updater=EloUpdater()
        ),
        game_simulator=GameSimulator(),

        population_size=60000,
        n_iterations=10
    ).evaluate()
    pass
