import json
import sys
import os
import log
from phub import Client as PhubClient
from phub.locals import Quality
from stashapi.stashapp import StashInterface

DOWNLOAD_LOCATION = "DOWNLOAD_LOCATION"


def print_download_progress(current_segment, total_segment):
    """Prints the download progress at every 10% interval."""
    percentage = (current_segment / total_segment) * 100
    if percentage % 10 == 0:
        log.LogInfo(f"Download progress: {round(percentage)}%")


def is_valid_scene_url(url):
    """Validates if the scene URL is from Pornhub and contains a viewkey."""
    return "pornhub.com" in url and "viewkey=" in url


def download_video(url):
    """Downloads the video from the URL, returns the Video object and download path, or (None, None)."""
    ph_client = PhubClient()
    video = ph_client.get(url)
    if video is None:
        return None, None
    dl_path = video.download(
        DOWNLOAD_LOCATION, Quality.BEST, display=print_download_progress
    )
    return video, dl_path


def update_and_merge_scenes(client, original_scene_id, video, dl_path):
    """Updates and merges the scene data in the Stash database."""
    clean_date = video.date.strftime("%Y-%m-%d")
    scene_update_data = {
        "id": original_scene_id,
        "url": video.url,
        "title": video.title,
        "date": clean_date,
    }
    client.update_scene(scene_update_data)

    dl_path_name = os.path.basename(dl_path)
    created_scenes = client.find_scenes(
        {"path": {"value": dl_path_name, "modifier": "INCLUDES"}}
    )
    if not created_scenes:
        return False

    created_scene_id = created_scenes[0].get("id")
    if not created_scene_id:
        return False

    client.merge_scenes(created_scene_id, original_scene_id)
    return True


def process_scene(client, scene):
    """Processes a single scene."""
    scene_id = scene.get("id")
    scene_url = scene.get("urls", [None])[0]
    if not scene_url or not is_valid_scene_url(scene_url):
        log.LogError(f"Invalid scene URL: {scene_url}")
        return False

    video, dl_path = download_video(scene_url)
    if not video or not dl_path:
        log.LogError(f"Failed to download video: {scene_url}")
        return False

    if not client.wait_for_job(client.metadata_scan()):
        log.LogError("Failed to scan for new files")
        return False

    if not update_and_merge_scenes(client, scene_id, video, dl_path):
        log.LogError(f"Failed to find or merge scene: {dl_path}")
        return False

    generate_params = {
        "covers": True,
        "sprites": True,
        "previews": True,
        "imagePreviews": True,
        "phashes": True,
        "clipPreviews": True,
        "sceneIDs": [scene_id],
    }
    if not client.wait_for_job(client.metadata_generate(generate_params)):
        log.LogError("Failed to generate content")
        return False

    return True


def main():
    json_input = json.loads(sys.stdin.read())
    stash = StashInterface(json_input["server_connection"])

    hook_context = json_input["args"].get("hookContext")
    if hook_context:
        scene_id = hook_context["id"]
        scene = stash.find_scene(scene_id)
        if not scene:
            log.LogError(f"Scene not found: {scene_id}")
            return

        log.LogInfo(f"Running for scene: {scene_id}")

        if process_scene(stash, scene):
            log.LogInfo(f"Successfully processed scene: {scene_id}")
        else:
            log.LogError(f"Failed to process scene: {scene_id}")

    log.LogInfo("Finished PH Full Auto")


main()
