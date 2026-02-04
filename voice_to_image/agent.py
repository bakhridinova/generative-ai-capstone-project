import re
import tempfile
from pathlib import Path
import requests
from openai import OpenAI
import openai
from utils import setup_logging


log = setup_logging()


class AudioToImagePipeline:

    RESTRICTED_TERMS = {
        "attack", "blood", "body", "crime", "dead", "death", "drug", "explicit",
        "fight", "gun", "hate", "injury", "kill", "murder", "naked", "politic",
        "racist", "religion", "sex", "shoot", "suicide", "terror", "violence", "war", "weapon"
    }

    def __init__(self, api_key: str):
        log.info("Initializing AudioToImagePipeline")
        self._api_client = OpenAI(api_key=api_key)
        self._temp_dir = Path(tempfile.gettempdir())

    def convert_speech_to_text(self, audio_data: bytes, audio_filename: str = "audio.wav") -> str:
        temp_audio_path = None
        try:
            log.info(f"Starting speech transcription | Audio size: {len(audio_data)} bytes")

            temp_audio_path = self._temp_dir / audio_filename
            temp_audio_path.write_bytes(audio_data)

            with temp_audio_path.open("rb") as audio_stream:
                log.info("Sending audio to Whisper API")
                api_response = self._api_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_stream,
                    response_format="text",
                    language="en"
                )
            
            transcribed_text = (
                api_response.strip()
                if isinstance(api_response, str)
                else api_response.text.strip()
            )

            log.info(f"Transcription successful | Preview: {transcribed_text[:60]}...")
            return transcribed_text

        except Exception as error:
            log.error(f"Speech transcription error: {error}", exc_info=True)
            raise RuntimeError(f"Unable to transcribe audio: {error}")

        finally:
            if temp_audio_path and temp_audio_path.exists():
                try:
                    temp_audio_path.unlink()
                except OSError:
                    pass

    def _apply_content_filter(self, raw_text: str) -> str:
        log.debug(f"Applying content filter | Input preview: {raw_text[:60]}...")

        filtered_text = raw_text.lower()

        for restricted_word in self.RESTRICTED_TERMS:
            pattern = rf"\b{restricted_word}\b"
            filtered_text = re.sub(pattern, "", filtered_text, flags=re.IGNORECASE)

        filtered_text = re.sub(r"[^a-zA-Z0-9\s,\.]", "", filtered_text)
        filtered_text = re.sub(r"\s+", " ", filtered_text).strip()

        safe_prompt = f"A friendly, creative and artistic interpretation of: {filtered_text}"

        log.debug(f"Filter applied | Output preview: {safe_prompt[:60]}...")
        return safe_prompt

    def optimize_for_image_generation(self, basic_description: str) -> str:
        try:
            log.info("Beginning prompt optimization via GPT-3.5-turbo")

            system_instructions = (
                "You are a specialized AI prompt architect for image generation systems. "
                "Transform user descriptions into highly detailed, vivid prompts that maximize "
                "DALL-E 3's capabilities. Include artistic style, lighting details, composition, "
                "color palette, and mood. Be specific and creative. Limit to 150 words."
            )

            user_message = (
                f"Transform this voice description into an optimized DALL-E prompt:\n\n"
                f"{basic_description}"
            )

            api_response = self._api_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            optimized_prompt = api_response.choices[0].message.content.strip()
            log.info(f"Prompt optimization complete | Preview: {optimized_prompt[:60]}...")
            return optimized_prompt

        except Exception as error:
            log.error(f"Prompt optimization error: {error}", exc_info=True)
            raise RuntimeError(f"Unable to optimize prompt: {error}")

    def synthesize_image(self, image_description: str) -> bytes:
        try:
            safe_description = self._apply_content_filter(image_description)
            
            log.info("Requesting image from DALL-E 3")
            print(f"[PIPELINE] Generating with prompt: {safe_description[:100]}...")
            
            generation_response = self._api_client.images.generate(
                model="dall-e-3",
                prompt=safe_description,
                size="1024x1024",
                quality="hd"
            )
            
            image_url = generation_response.data[0].url
            log.info("Image generated successfully")
            print("[PIPELINE] Image generation completed")

            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            return image_response.content
            
        except openai.BadRequestError as policy_error:
            log.warning(f"Content policy violation detected: {policy_error}")
            print("[PIPELINE] Content filter triggered - attempting safe fallback...")
            
            return self._generate_fallback_image()

        except Exception as error:
            log.error(f"Image generation error: {error}", exc_info=True)
            raise RuntimeError(f"Unable to generate image: {error}")

    def _generate_fallback_image(self) -> bytes:
        fallback_description = (
            "A serene, abstract artistic landscape featuring soft pastel colors, "
            "gentle lighting, and peaceful composition with harmonious elements."
        )
        
        try:
            log.info("Attempting fallback image generation")

            fallback_response = self._api_client.images.generate(
                model="dall-e-3",
                prompt=fallback_description,
                size="1024x1024",
                quality="hd"
            )
            
            fallback_url = fallback_response.data[0].url
            log.info("Fallback image generated successfully")
            print("[PIPELINE] Fallback image generated")

            image_response = requests.get(fallback_url, timeout=30)
            image_response.raise_for_status()
            return image_response.content
            
        except Exception as fallback_error:
            log.error(f"Fallback generation failed: {fallback_error}", exc_info=True)
            raise RuntimeError(
                f"Both primary and fallback generation failed: {fallback_error}"
            )

