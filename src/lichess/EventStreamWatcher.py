import json
import logging
from src.lichess.ContinuousWorker import ContinuousWorker

logger = logging.getLogger(__name__)

class EventStreamWatcher(ContinuousWorker):
    def __init__(self, lichess_api, game_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = lichess_api
        self.game_manager = game_manager
        self.username = self.api.get_profile().json()["username"]

    def work(self):
        event_stream = self.api.stream_events()

        for line in event_stream:
            if line:
                logger.debug(f"From event stream: {json.loads(line)}")
                line = json.loads(line)
                self._dispatch_event_action(line)
    
    def _dispatch_event_action(self, line):
        event_type = line["type"]
        if event_type == "challenge":
            # The ChallengeHandler class handles all incoming and outgoing challenges, so we will skip this event type.
            # The reason for this is because the Lichess API has two different streams for "Events" and "Challenges"
            pass
        elif event_type == "challengeDeclined":
            pass
        elif event_type == "gameStart":
            logger.info("Starting a new game.")
            game_started = self.game_manager.start_new_game(line)
            if (not game_started):
                # TODO: decline/abort the game
                pass
        elif event_type == "gameFinish":
            self.game_manager.terminate_game(line["game"]["fullId"])
        elif event_type == "challengeCancelled":
            pass
        else:
            pass

    def _cleanup(self):
        # TODO: Cleanup resources
        return