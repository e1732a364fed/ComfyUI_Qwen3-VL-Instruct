import cv2


class MultiplePathsInput:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "inputcount": ("INT", {"default": 1, "min": 1, "max": 1000, "step": 1}),
                "path_1": ("PATH",),
            },
            "optional": {
                "sample_fps": ("INT", {"default": 1, "min": 1, "max": 1000, "step": 1}),
                "max_frames": (
                    "INT",
                    {"default": 2, "min": 2, "max": (1 << 63) - 1, "step": 1},
                ),
                "use_total_frames": ("BOOLEAN", {"default": True}),
                "use_original_fps_as_sample_fps": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("PATH",)
    RETURN_NAMES = ("paths",)
    FUNCTION = "combine"
    CATEGORY = "Comfyui_Qwen3-VL-Instruct"
    DESCRIPTION = """
Creates a path batch from multiple paths.
You can set how many inputs the node has,
with the **inputcount** and clicking update.
"""

    @staticmethod
    def convert_path_to_json(
        file_path,
        sample_fps=1,
        max_frames=1,
        use_total_frames=True,
        use_original_fps_as_sample_fps=True,
    ):
        ext = file_path.split(".")[-1].lower()

        if ext in ["jpg", "jpeg", "png", "bmp", "tiff", "webp"]:
            return {"type": "image", "image": f"{file_path}"}
        elif ext in ["mp4", "mkv", "mov", "avi", "flv", "wmv", "webm", "m4v"]:
            print("source_video_path:", file_path)
            # vr = VideoReader(file_path, ctx=cpu(0))
            vidObj = cv2.VideoCapture(file_path)
            vr = []
            while vidObj.isOpened():
                ret, frame = vidObj.read()
                if not ret:
                    break
                else:
                    vr.append(frame)
            total_frames = len(vr) + 1
            print("Total frames:", total_frames)
            avg_fps = vidObj.get(cv2.CAP_PROP_FPS)
            print("Get average FPS(frame per second):", avg_fps)
            duration = len(vr) / avg_fps
            print("Total duration:", duration, "seconds")
            width = vr[0].shape[1]
            height = vr[0].shape[0]
            print("Video resolution(width x height):", width, "x", height)
            vidObj.release()
            return {
                "type": "video",
                "video": f"{file_path}",
                "fps": avg_fps if use_original_fps_as_sample_fps else sample_fps,
                "max_frames": total_frames if use_total_frames else max_frames,
            }
        else:
            return None

    def combine(self, inputcount, **kwargs):
        path_list = []
        for c in range(inputcount):
            path = kwargs[f"path_{c + 1}"]

            filtered_kwargs = {
                k: v for k, v in kwargs.items() if not k.startswith("path_")
            }

            path = self.convert_path_to_json(path, **filtered_kwargs)
            print(path)
            path_list.append(path)
        print(path_list)
        result = path_list
        return (result,)
