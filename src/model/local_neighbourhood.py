from typing import Dict, List
import json
import random


class LocalNeighbourhood():
    """
    A class which represents a bluesky local local neighbourhood
    """

    def __init__(self, seed_id: str, params, users: Dict, user_activity: str="unknown"):
        self.seed_id = seed_id
        self.params = params
        self.users = users
        self.user_activity = user_activity

    def get_user_id_list(self) -> List:
        return list(self.users.keys())

    def get_user_activities(self, id, sample_prop: float=1.0) -> List:
        if id in self.users:
            user_activities = self.users[id]
            if sample_prop == 1.0:
                return user_activities
            # randomly sample the user's activities
            num_activities = len(user_activities)
            num_sampled_activities = int(num_activities * sample_prop)
            return random.sample(user_activities, num_sampled_activities)
        else:
            return []
        
    def get_user_activity(self) -> str:
        return self.user_activity

    def toJSON(self) -> str:
        """
        Returns a json corresponding to the given localNeighbourhood object

        @return a json representation of the localNeighbourhood
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
            indent=4)

    def fromJSON(json_in: str):
        """
        Given a json representation of a local neighbourhood, return the
        local neighbourhood object

        @param json_in the json to convert to a LocalNeighbourhood

        @return the LocalNeighbourhood object
        """
        obj = json.loads(json_in)
        localNeighbourhood = LocalNeighbourhood(
            obj.get("seed_id"),
            obj.get("params"),
            obj.get("users"),
            obj.get("user_activity")
        )

        return localNeighbourhood

    def fromDict(dict: Dict):

        localNeighbourhood = LocalNeighbourhood(
            dict["seed_id"], dict["params"], dict["users"], dict["user_activity"]
        )

        return localNeighbourhood

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
