import os
import aiohttp
from typing import List, Optional

class BRollManager:
    PEXELS_API_URL = "https://api.pexels.com/videos/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            print("Warning: PEXELS_API_KEY not set. B-roll video search will not work.")
        self.session = None

    async def _create_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers={"Authorization": self.api_key})

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_clips_for_keywords(self, keywords: List[str], max_clips: int = 3) -> List[str]:
        if not self.api_key:
            print("No Pexels API key provided; cannot fetch B-roll clips.")
            return []

        await self._create_session()

        selected_clips = []
        seen_urls = set()

        for kw in keywords:
            params = {
                "query": kw,
                "per_page": max_clips,
                "orientation": "landscape"
            }
            try:
                async with self.session.get(self.PEXELS_API_URL, params=params) as resp:
                    if resp.status != 200:
                        print(f"Pexels API request failed for keyword '{kw}' with status {resp.status}")
                        continue
                    data = await resp.json()
                    videos = data.get("videos", [])
                    for video in videos:
                        video_files = video.get("video_files", [])
                        if not video_files:
                            continue
                        best_file = max(video_files, key=lambda f: f.get("width", 0))
                        video_url = best_file.get("link")
                        if video_url and video_url not in seen_urls:
                            selected_clips.append(video_url)
                            seen_urls.add(video_url)
                            if len(selected_clips) >= max_clips:
                                await self.close()
                                return selected_clips
            except Exception as e:
                print(f"Error fetching B-roll clips for keyword '{kw}': {e}")

        await self.close()
        return selected_clips
