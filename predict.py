# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input, Path
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    VideoFileClip,
)
import moviepy.video.fx.all as vfx


class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        # self.model = torch.load("./weights.pth")

    def predict(
        self,
        image: Path = Input(description="Grayscale input image", default=None),
        image2: Path = Input(description="Second image", default=None),
        image3: Path = Input(description="Third image", default=None),
        image4: Path = Input(description="Fourth image", default=None),
        video: Path = Input(description="Grayscale input image", default=None),
        video2: Path = Input(description="Second image", default=None),
        video3: Path = Input(description="Third image", default=None),
        video4: Path = Input(description="Fourth image", default=None),
        audio: Path = Input(description="Audio file"),
    ) -> Path:
        """Run a single prediction on the model"""
        if image:
            return self.predict_image(image, image2, image3, image4, audio)
        elif video:
            return self.predict_video(video, video2, video3, video4, audio)
        else:
            raise ValueError("No input provided")

    def predict_image(self, image, image2, image3, image4, audio):
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
        final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        return Path(output_path)

    def predict_video(self, video, video2, video3, video4, audio):
        audio_path = str(audio)
        audio_clip = AudioFileClip(audio_path)

        videos = [str(video)]
        if video2:
            videos.append(str(video2))
        if video3:
            videos.append(str(video3))
        if video4:
            videos.append(str(video4))

        video_clip_duration = audio_clip.duration / len(videos)

        final_clips = []
        for video_path in videos:
            video_clip = VideoFileClip(video_path)
            reversed_clip = video_clip.fx(vfx.time_mirror)
            symmetrized_clip = concatenate_videoclips([video_clip, reversed_clip])

            video_clips = [symmetrized_clip.loop(duration=video_clip_duration)]
            final_video_clip = concatenate_videoclips(video_clips)
            final_clips.append(final_video_clip)

        final_video = concatenate_videoclips(final_clips)
        final_video = final_video.set_audio(audio_clip)
        output_path = "/tmp/output.mp4"
        final_video.write_videofile(
            output_path, fps=24, codec="libx264", audio_codec="aac"
        )
        return Path(output_path)
