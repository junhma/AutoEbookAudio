# AutoEbookAudio

A script to automatically generate ebook audios with edge-tts

## Requirements

pip install pandas asyncio edge_tts

## Steps

1. Put `input.epub` file in the `korean_files_python` folder.
2. Run `async_audio_gen_with_predefined_voice`.

## Korean Voices

| Name                           | Gender | Use     | Characteristics    |
| ------------------------------ | ------ | ------- | ------------------ |
| ko-KR-HyunsuMultilingualNeural | Male   | General | Friendly, Positive |
| ko-KR-InJoonNeural             | Male   | General | Friendly, Positive |
| ko-KR-SunHiNeural              | Female | General | Friendly, Positive |

InJoonNeural max 4 hours  
SunHiNeural max 12 hrs/~10,000 lines
