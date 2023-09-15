import typing as T
import uuid
import random
from concurrent.futures import ThreadPoolExecutor

from .elo import rate_1vs1, INITIAL


class Matchmaker:
    def __init__(
        self,
        game_team_count = 20,  # number team per game
        game_time_size = 3,  # population size per team) -> None:
    ):
        self.game_team_count = game_team_count
        self.game_time_size = game_time_size

    def create_games(
        self,
        population: T.List[dict]
    ):
        population.sort(key=lambda m: m["elo"])
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
        lobbies = [
            list(
                zip(
                    *[
                        lobby[i::self.game_time_size]
                        for i in range(self.game_time_size)
                    ]
                )
            )
            for lobby in lobbies
        ]
        return lobbies


class EloUpdater:
    def __init__(self) -> None:
        pass

    def update_elos(
        self,
        population: T.List[dict],
        results: list
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
    def simulate_games(self, games: list):
        game_count = len(games)
        simulated_games = []
        with ThreadPoolExecutor(game_count) as executor:
            for result in executor.map(
                lambda game: self._simulate_game(game),
                games
            ):
                simulated_games.append(result)
        return simulated_games

    def _simulate_game(self, game: list):
        """
        Simulate real person performance based on member
            skill_level
        """
        winners = list(game)
        losers = []
        while len(losers) < len(game) - 1:
            random.shuffle(winners)
            winners = sorted(winners, key=lambda d: d is None)
            for i in range(0, len(winners), 2):
                team1 = winners[i]
                team2 = winners[i+1]
                if not team1 or not team2:
                    continue

                winner_team, loser_team = self._simulate_team_battle(
                    team1,
                    team2
                )
                winners[winners.index(loser_team)] = None
                losers.insert(0, loser_team)

        winners = sorted(winners, key=lambda d: d is None)
        return [
            winners[0],
            *losers
        ]


    def _simulate_team_battle(self, team1: T.List[dict], team2: T.List[dict]):
        team1_copy = list(team1)
        team2_copy = list(team2)

        while any(team1_copy) and any(team2_copy):
            random.shuffle(team1_copy)
            team1_copy = sorted(team1_copy, key=lambda d: d is None)
            random.shuffle(team2_copy)
            team2_copy = sorted(team2_copy, key=lambda d: d is None)
            for player1, player2 in zip(team1_copy, team2_copy):
                if not player1 or not player2:
                    continue

                winner_player, loser_player = self._simulate_player_battle(
                    player1,
                    player2
                )
                winner_player["elo"], loser_player["elo"] = rate_1vs1(winner_player["elo"], loser_player["elo"])
                winner_player["kill_count"] = winner_player.get("kill_count", 0) + 1
                loser_player["death_count"] = loser_player.get("death_count", 0) + 1
                # remove loser from the team
                for team in [team1_copy, team2_copy]:
                    try:
                        team[team.index(loser_player)] = None
                    except ValueError:
                        pass

        if any(team1_copy):
            return team1, team2

        return team2, team1
    
    def _simulate_player_battle(self, player1: dict, player2: dict):
        player1_skill = player1["skill_level"]
        player2_skill = player2["skill_level"]

        prob_player1_win = player1_skill / (player1_skill + player2_skill)
        if random.random() < prob_player1_win:
            return player1, player2
        return player2, player1


class RankedSystemEvaluator:
    def __init__(
        self,
        ranked_system: RankedSystem,
        game_simulator: GameSimulator,
        population_size: int,
        n_iterations: int
    ):
        self.ranked_system = ranked_system
        self.game_simulator = game_simulator

        self.population_size = population_size
        self.n_iterations = n_iterations

    def evaluate(self):
        population = self.create_population()
        for _ in range(self.n_iterations):
            games = self.ranked_system.matchmaker.create_games(population)
            results = self.game_simulator.simulate_games(games)
            self.ranked_system.elo_updater.update_elos(
                population=population,
                results=results
            )
        return population

    def create_member(self) -> dict:
        return {
            "_id": str(uuid.uuid4()),
            "skill_level": random.random(),
            "elo": INITIAL
        }

    def create_population(self) -> T.List[dict]:
        return [self.create_member() for _ in range(self.population_size)]
