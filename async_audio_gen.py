import glob
import os
import asyncio
import time
import edge_tts
import subprocess
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

def epub_to_txt(epub_file: str, epub_output_file: str):
    """
    Convert an epub file to a txt file

    :param epub_file: The directory for the epub file.
    :param epub_output_file: The directory for the output txt file.
    """
    command_list = [
        'pandoc',
        str(epub_file),
        '-f', 'epub',        # Specifies the input format (From: epub)
        '-t', 'plain',       # Specifies the output format (To: plain text)
        '-s',                # Produce a standalone document
        '-o', str(epub_output_file), # Specifies the output file path
        '--wrap=none'        # Disables text wrapping
    ]
    try:
        subprocess.run(
            command_list, 
            check=True,  # Raises CalledProcessError on failure
            capture_output=True, 
            text=True
        )
    except Exception as e:
        logger.error(e)
        raise

def split_txt(
    full_txt_file_path: str | Path, 
    line_number: int, 
    output_dir_path: str | Path, 
    file_prefix: str = "part_"):
    """
    Splits a large text file into smaller files by line count, 
    saves them to a target directory, and ensures they end with .txt.

    :param full_txt_file_path: Path to the large text file.
    :param line_number: The number of lines for each smaller file.
    :param output_dir_path: The directory for the split files.
    :param file_prefix: The prefix for the split file names (e.g., 'part_').
    """
    output_dir = Path(output_dir_path)
    full_txt_file = Path(full_txt_file_path)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(e)
        raise
    output_prefix = output_dir / file_prefix
    command_list = [
        'split',
        '-l', str(line_number),
        '-d',      # Use numeric suffixes (000, 001, 002...)
        '-a', '3', # Use a 3-digit suffix length
        str(full_txt_file),
        str(output_prefix)
    ]
    try:
        subprocess.run(
            command_list, 
            check=True,  # Raises CalledProcessError on failure
            capture_output=True, 
            text=True
        )
        pattern = str(output_dir / f'{file_prefix}*')
        split_files = glob.glob(pattern)
        for old_path_str in split_files:
            old_path = Path(old_path_str)
            if old_path.suffix != '.txt':
                new_path = old_path.with_suffix('.txt')
                old_path.rename(new_path)
        logger.info(f"Successfully split '{full_txt_file.name}' into .txt files in '{output_dir}'")
    except Exception as e:
        logger.error(e)
        raise

def load_file(folder_path: str) -> dict:
    """
    Load all the splitted txt files from the given folder into a dictionary

    :param folder_path: the path of the folder that holds all the splitted txt files
    :return: a dict in the format of file_name: content
    """
    file_contents_dict = {}
    file_pattern = os.path.join(folder_path, '*.txt')
    file_paths = glob.glob(file_pattern)
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                file_contents_dict[file_name] = content
        except Exception as e:
            logger.error(e)
            raise
    return file_contents_dict

async def generate_audio(text: str, voice: str, audio_file: str, subtitle_file: str):
    """Generates a single audio file."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(audio_file)
    communicate = edge_tts.Communicate(text, text)
    submaker = edge_tts.SubMaker()
    with open(audio_file, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)

    with open(subtitle_file, "w", encoding="utf-8") as file:
        file.write(submaker.get_srt())
    print(f"Finished generating {audio_file}")

async def main():
    """Main function to run concurrent audio generation."""
    logging.basicConfig(filename='async_audio_gen.log', level=logging.INFO)
    logger.info('Started')
    TXT_FOLDER_PATH = 'ebook_txt'
    MP3_FOLDER_PATH = 'ebook_audio'
    SUBTITLES_FOLDER_PATH = 'ebook_subtitles'
    VOICE = "ko-KR-SunHiNeural"
    AUDIO_EXTENSION = ".mp3"
    SUBTITLE_EXTENSION = ".srt"
    INPUT_FILE = 'input.epub'
    # name of the txt file converted from input.epub
    EPUB_OUTPUT_FILE = "output.txt"
    #split EPUB_OUTPUT_FILE into smaller txt files, each with LINE_NUMBER amount of lines
    LINE_NUMBER = 20000 
    try:
        start_time = time.time()
        tasks = []
        epub_to_txt(INPUT_FILE, EPUB_OUTPUT_FILE)
        split_txt(EPUB_OUTPUT_FILE, LINE_NUMBER, TXT_FOLDER_PATH)

        item_dict = load_file(TXT_FOLDER_PATH)

        for base_name, content in item_dict.items():
            base_name_without_txt = os.path.splitext(base_name)[0]
            audio_filename_with_ext = f"{base_name_without_txt}{AUDIO_EXTENSION}"
            audio_file = os.path.join(MP3_FOLDER_PATH, audio_filename_with_ext)

            subtitle_filename_with_ext = f"{base_name_without_txt}{SUBTITLE_EXTENSION}"
            subtitle_file = os.path.join(SUBTITLES_FOLDER_PATH, subtitle_filename_with_ext)
            task = generate_audio(content, VOICE, audio_file, subtitle_file)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        print("All audio files have been generated.")
        print("--- %s seconds ---" % (time.time() - start_time))
        logger.info('Finished')
    except Exception as e:
            print(f"Error {e}")

if __name__ == "__main__":
    asyncio.run(main())
