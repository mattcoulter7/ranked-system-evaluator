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
        game_simulator=GameSimulator(128),
        sample_size=12000,
        epochs=20
    ).evaluate()
    pass
