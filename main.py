

from src.orchestrator.scheduler import GameCreationOrchestrator


def main():
    orchestrator = GameCreationOrchestrator()
    orchestrator.run_pipeline()


if __name__ == "__main__":
    main()

