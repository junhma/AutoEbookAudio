"""Unit tests for convert file format and update chapters."""

import unittest

from pathlib import Path
from async_audio_gen import generate_audio

class TestUpdate(unittest.IsolatedAsyncioTestCase):
    """Unit tests for edge-tts audio generation."""
    VOICE = "ko-KR-SunHiNeural"
    extensions = ["txt", "mp3", "srt"]
    files = {ext: Path.cwd() / "tests" / f"test.{ext}" for ext in extensions}
    with open(files['txt'], 'r') as file:
        file_content = file.read()

    async def test_generate_audio(self):
        """Tests if the audio and subtitles are generated properly."""
        await generate_audio(self.file_content, self.VOICE, self.files['mp3'], self.files['srt'])

if __name__ == '__main__':
    unittest.main()
