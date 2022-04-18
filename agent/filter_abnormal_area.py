import os
import gc
import time
import datetime
import re
from multiprocessing import Process
from time import sleep

import large_image
import numpy as np
import pandas as pd
from PIL import Image

from agent.settings import CONFIG, LOGGER
from agent.utils import get_slide_name


class FilterArea(Process):
    def __init__(self, src_file, des_folder):
        super().__init__()
        self.daemon = True
        self.src_file = src_file
        self.size = CONFIG["patch"]["size"]
        self.des_folder = des_folder

    def check_abnormal_area(self, image: np.ndarray):
        gray_img = image[..., 0]
        h, w = gray_img.shape
        if h != self.size or w != self.size:
            return False

        mask = (gray_img > 70) * (gray_img < 220)
        otsu_ratio = mask.sum() / np.multiply(*mask.shape)

        if otsu_ratio < 0.045:
            del gray_img
            del mask
            del otsu_ratio
            del image

            return False

        del gray_img
        del mask
        del otsu_ratio
        del image

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
        # save_path = os.path.join(
        #     self.des_folder,
        #     dir_name,
        #     slide_name,
        # )
        save_path = self.des_folder
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
                tile_image.close()
                
                #sleep(0.1)

                del tile_image
                del tile_info

            gc.collect()

        df.to_csv(os.path.join(save_path, f"{slide_name}.csv"), index=False)

        del ts
        del df
        LOGGER.info("Finished...")

    def run(self) -> None:
        try:
            start = time.time()
            self.check_iter_tiles(self.src_file)
            sec = time.time() - start
            times = str(datetime.timedelta(seconds=sec)).split(".")
            LOGGER.info(f"slide processing time: {times[0]}")

        except Exception as e:
            LOGGER.error(e)
