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
import os


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
        video_frames: int = Input(
            description="Number of frames to double", default=None
        ),
        audio: Path = Input(description="Audio file"),
    ) -> Path:
        """Run a single prediction on the model"""
        if image:
            return self.predict_image(image, image2, image3, image4, audio)
        elif video:
            return self.predict_video(
                video, video2, video3, video4, video_frames, audio
            )
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

    def predict_video(self, video, video2, video3, video4, video_frames, audio):
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

        if video_frames:
            doubled_frame_count = video_frames * 2
        else:
            doubled_frame_count = 50
        final_clips = []

        print(video_clip_duration)
        for index, video_path in enumerate(videos):
            print(video_path)
            os.system(
                'ffmpeg -i {0} -filter_complex "[0]reverse[r];[0][r]concat,loop=1:{2},setpts=N/55/TB" /tmp/newvideo-{1}.mp4 -y'.format(
                    video_path, index, doubled_frame_count
                )
            )

            video_clip = VideoFileClip("/tmp/newvideo-{0}.mp4".format(index))

            num_loops = int(video_clip_duration / video_clip.duration)
            remaining_duration = video_clip_duration % video_clip.duration

            looped_videos = []
            for i in range(num_loops):
                looped_videos.append(video_clip)
            final_video_clip = concatenate_videoclips(looped_videos)
            final_clips.append(final_video_clip)
            final_clips.append(video_clip.subclip(0, remaining_duration))

        final_video = concatenate_videoclips(final_clips)
        final_video = final_video.set_audio(audio_clip)
        output_path = "/tmp/output.mp4"
        final_video.write_videofile(
            output_path, fps=24, codec="libx264", audio_codec="aac"
        )
        return Path(output_path)
