import typing as T
import uuid
import random
from concurrent.futures import ThreadPoolExecutor

from .elo import rate_1vs1, INITIAL

class Player:
    _id: str = str(uuid.uuid4())
    skill_level: float = random.random()
    elo: float = INITIAL
    kill_count: int = 0
    death_count: int = 0


class Game:
    def __init__(self, teams: T.List[T.List[Player]]) -> None:
        self.teams = teams


class GameResult:
    def __init__(self, outcome: T.List[T.List[Player]]) -> None:
        self.outcome = outcome


class Matchmaker:
    def __init__(
        self,
        game_team_count: int = 20,  # number team per game
        game_time_size: int = 3,  # population size per team) -> None:
    ):
        self.game_team_count = game_team_count
        self.game_time_size = game_time_size

    def create_games(
        self,
        population: T.List[Player]
    ) -> T.List[Game]:
        population.sort(key=lambda m: m.elo)
        game_population_size = self.game_team_count * self.game_time_size

        # 1. build the lobbies
        lobbies = [
            population[i:i+game_population_size]
            for i in range(
                0,
                len(population),
                game_population_size
            )
        ]

        # 2. build the teams in each lobby
        return [
            Game(
                teams=list(
                    zip(
                        *[
                            lobby[i::self.game_time_size]
                            for i in range(self.game_time_size)
                        ]
                    )
                )
            )
            for lobby in lobbies
        ]


class EloUpdater:
    def __init__(self) -> None:
        pass

    def update_elos(
        self,
        population: T.List[Player],
        results: T.List[GameResult]
    ):
        for result in results:
            pass


class RankedSystem:
    def __init__(
        self,
        matchmaker: Matchmaker,
        elo_updater: EloUpdater,
    ):
        self.matchmaker = matchmaker
        self.elo_updater = elo_updater


class GameSimulator:
    def __init__(self, max_concurrency: int = 1):
        self.executor = ThreadPoolExecutor(max_concurrency)

    def simulate_games(self, games: T.List[Game]):
        return [
            result for result in self.executor.map(
                lambda game: self._simulate_game(game),
                games
            )
        ]

    def _simulate_game(self, game: Game) -> T.List[GameResult]:
        """
        Simulate real person performance based on player skill_level
        """
        outcome = []
        while len(outcome) < len(game.teams):
            team1, team2 = random.choices(game.teams, k=2)

            winner_team, loser_team = self._simulate_team_battle(
                team1, team2
            )
            outcome.insert(0, loser_team)
            if len(outcome) == len(game.teams) - 1:
                outcome.insert(0, winner_team)

        return GameResult(
            outcome=outcome
        )


    def _simulate_team_battle(self, team1: T.List[Player], team2: T.List[Player]):
        team1_copy = sorted(team1, key=lambda _: random.random())
        team2_copy = sorted(team2, key=lambda _: random.random())

        while len(team1_copy) and len(team2_copy):
             player1, player2 = team1_copy.pop(), team2_copy.pop()

             winner_player, loser_player = self._simulate_player_battle(
                player1, player2
             )

             winner_player.elo, loser_player.elo= rate_1vs1(winner_player.elo, loser_player.elo)
             winner_player.kill_count += 1
             loser_player.death_count += 1

             if winner_player in team1:
                team1_copy.insert(random.randint(0, len(team1_copy)), winner_player)
             elif winner_player in team2:
                team2_copy.insert(random.randint(0, len(team2_copy)), winner_player)

        return (team1, team2) if len(team1_copy) else (team2, team1)
    
    def _simulate_player_battle(self, player1: Player, player2: Player):
        player1_skill = player1.skill_level
        player2_skill = player2.skill_level

        prob_player1_win = player1_skill / (player1_skill + player2_skill)
        if random.random() < prob_player1_win:
            return player1, player2
        return player2, player1


class RankedSystemEvaluator:
    def __init__(
        self,
        ranked_system: RankedSystem,
        game_simulator: GameSimulator,
        sample_size: int,
        epochs: int
    ):
        self.ranked_system = ranked_system
        self.game_simulator = game_simulator

        self.sample_size = sample_size
        self.epochs = epochs

    def evaluate(self):
        population = self._create_population()
        for epoch in range(self.epochs):
            print(f"Epoch [{epoch+1}/{self.epochs}]")
            games = self.ranked_system.matchmaker.create_games(population)
            results = self.game_simulator.simulate_games(games)
            self.ranked_system.elo_updater.update_elos(
                population=population,
                results=results
            )
        return population

    def _create_population(self) -> T.List[Player]:
        return [Player() for _ in range(self.sample_size)]
