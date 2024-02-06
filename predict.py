# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input, Path
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx


class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        # self.model = torch.load("./weights.pth")

    def predict(
        self,
        image: Path = Input(description="Grayscale input image"),
        image2: Path = Input(description="Second image", default=None),
        image3: Path = Input(description="Third image", default=None),
        image4: Path = Input(description="Fourth image", default=None),
        audio: Path = Input(description="Audio file"),
    ) -> Path:
        """Run a single prediction on the model"""
        audio_path = str(audio)
        audio_clip = AudioFileClip(audio_path)

        images = [str(image)]
        if image2:
            images.append(str(image2))
        if image3:
            images.append(str(image3))
        if image4:
            images.append(str(image4))

        image_clip_duration = audio_clip.duration / len(images)

        video_clips = []
        for image in images:
            video_clip = ImageClip(image, duration=image_clip_duration)
            video_clips.append(video_clip)
        final = concatenate_videoclips(video_clips)
        final = final.set_audio(audio_clip)
        output_path = "/tmp/output.mp4"
        final.write_videofile(
            output_path, fps=24, codec="libx264", audio_codec="aac"
        )
        return Path(output_path)