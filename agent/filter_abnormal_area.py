import os
import time
import datetime
from multiprocessing import Process

import large_image
import numpy as np
import pandas as pd
from PIL import Image

from agent.settings import CONFIG, LOGGER
from agent.utils import get_slide_name


class FilterArea(Process):
    def __init__(self, file_list):
        super().__init__()
        self.daemon = True
        self.file_list = file_list
        self.size = CONFIG["patch"]["size"]

    def check_abnormal_area(self, image: np.ndarray):
        gray_img = image[..., 0]

        mask = (gray_img > 70) * (gray_img < 220)
        otsu_ratio = mask.sum() / np.multiply(*mask.shape)

        if otsu_ratio < 0.045:
            del gray_img
            del mask
            del otsu_ratio

            return False

        del gray_img
        del mask
        del otsu_ratio

        return True

    def check_iter_tiles(self, file_path):
        LOGGER.info("Start..")
        df = pd.DataFrame(
            columns=[
                "tile_name",
                "original_x",
                "original_y",
                "magnification",
                "level",
                "tile_position",
                "tile_size",
                "tile_x",
                "tile_y",
            ]
        )
        slide_name, _ = get_slide_name(file_path)
        dir_name = os.path.dirname(file_path).split("/")[-1]
        save_path = os.path.join(
            CONFIG["path"]["save"],
            dir_name,
            slide_name,
        )
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        ts = large_image.getTileSource(file_path)
        ts_metadata = ts.getMetadata()
        magnification = ts_metadata.get("magnification")
        slide_size = ts_metadata.get("sizeX"), ts_metadata.get("sizeY")

        for tile_info in ts.tileIterator(
            scale=dict(magnification=magnification),
            tile_size=dict(width=self.size, height=self.size),
        ):
            tile_image = tile_info["tile"]
            position = tile_info["tile_position"]["position"]

            h, w = tile_image[..., 0].shape
            if w != self.size or h != self.size:
                canvas = np.zeros((self.size, self.size, 3), np.uint8)
                canvas.fill(255)
                canvas[:h, :w] = tile_image
                tile_image = canvas
                del canvas

            if self.check_abnormal_area(tile_image):
                tile_name = f"{slide_name}_{position}.png"
                df.loc[len(df)] = {
                    "tile_name": tile_name,
                    "original_x": slide_size[0],
                    "original_y": slide_size[1],
                    "magnification": ts_metadata.get("magnification"),
                    "level": tile_info["level"],
                    "tile_position": position,
                    "tile_size": self.size,
                    "tile_x": tile_info["x"],
                    "tile_y": tile_info["y"],
                }

                tile_save_path = os.path.join(save_path, tile_name)
                tile_image = Image.fromarray(tile_image)
                tile_image.save(tile_save_path)

                del tile_image

        df.to_csv(os.path.join(save_path, f"{slide_name}.csv"), index=False)

        del ts
        del df
        LOGGER.info("Finished...")

    def run(self) -> None:
        try:
            for file in self.file_list:
                start = time.time()
                self.check_iter_tiles(file)
                sec = time.time() - start
                times = str(datetime.timedelta(seconds=sec)).split(".")
                LOGGER.info(f"slide processing time: {times[0]}")

        except Exception as e:
            LOGGER.error(e)
