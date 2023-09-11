from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy
from pydub import AudioSegment
import os

def generate_music():
    # Initialize the processor and model
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

    # Prepare inputs
    inputs = processor(
        text=["Magical enchanting music pop music exciting epic adventure magical fantasy"],
        padding=True,
        return_tensors="pt",
    )

    # Generate audio
    audio_values = model.generate(**inputs, max_new_tokens=512)

    # Save as WAV file
    sampling_rate = model.config.audio_encoder.sampling_rate
    scipy.io.wavfile.write("musicgen_out.wav", rate=sampling_rate, data=audio_values[0, 0].numpy())

    # Convert WAV to MP3
    wav_audio = AudioSegment.from_wav("musicgen_out.wav")
    wav_audio.export("musicgen_out.mp3", format="mp3")

    # Delete the WAV file
    os.remove("musicgen_out.wav")