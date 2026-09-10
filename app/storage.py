# make a fakestorage to be able to test without an actual cloudservice
class FakeStorage:
    def presigned_put(self, key: str) -> str:
        return f"https://fake-storage.local/put/{key}"

    def presigned_get(self, key: str) -> str:
        return f"https://fake-storage.local/get/{key}"


def get_storage():
    return FakeStorage()


def video_key_for(match_id: str) -> str:
    return f"matches/{match_id}/raw.mp4"
