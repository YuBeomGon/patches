import os
import time
import datetime
from multiprocessing import Process

import cv2
import large_image
import numpy as np
from PIL import Image

from agent.utils import get_slide_name
from agent.settings import CONFIG, LOGGER


class FilterArea(Process):
    def __init__(self, file_list):
        super().__init__()
        self.daemon = True
        self.file_list = file_list
        self.size = CONFIG["patch"]["size"]

    def check_abnormal_area(self, image: np.ndarray):
        # alpha = 0.7
        # beta = 0.3

        gray_img = image[..., 0]

        mask = (gray_img > 70) * (gray_img < 220)
        otsu_ratio = mask.sum() / np.multiply(*mask.shape)

        if otsu_ratio < 0.045:
            return False, None

        # _, thresh = cv2.threshold(gray_img, 230, 255, cv2.THRESH_BINARY_INV)
        #
        # contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # contours = list(filter(lambda x: len(x) > 3, contours))
        # if not contours:
        #     return False, None
        #
        # contour_sizes = np.array(list(map(cv2.contourArea, contours)))
        #
        # if (contour_sizes > 40000).any():
        #     return False, None

        # num_contours = len(contour_sizes)
        # mean_size = np.mean(contour_sizes)
        #
        # score = (alpha * num_contours) + (beta * mean_size)
        #
        # return True, score
        return True, None

    def get_filtered_index(self, ts) -> list:
        ts_metadata = ts.getMetadata()
        tile_count = ts.getTileCount(tile_size=dict(width=self.size, height=self.size))
        scores = []

        for tile_info in ts.tileIterator(
            scale=dict(magnification=ts_metadata.get("magnification")),
            tile_size=dict(width=self.size, height=self.size),
        ):
            tile_image = tile_info["tile"]
            tile_image = Image.fromarray(tile_image)
            tile_image = np.array(tile_image.convert("RGB"))

            # if tile image size < (size, size, 3) -> fill white color in blank areas
            h, w = tile_image[..., 0].shape
            if w != self.size or h != self.size:
                canvas = np.zeros((self.size, self.size, 3), np.uint8)
                canvas.fill(255)
                canvas[:h, :w] = tile_image
                tile_image = canvas

            tile_image = cv2.resize(tile_image, (512, 512))

            # [tile position, tile score] 식으로 저장
            check, score = self.check_abnormal_area(tile_image)
            if check:
                # scores.append([tile_info["tile_position"]["position"], score])
                scores.append(tile_info["tile_position"]["position"])
            else:
                continue

        # score 기준으로 sorting
        # scores.sort(key=lambda x: x[1], reverse=True)
        #
        # # 15% 만 저장
        # num_15p = int(tile_count * 0.15)
        # return scores[:num_15p]
        return scores

    def check_iter_tiles(self, file_path):
        LOGGER.info("Scoring...")
        slide_name, _ = get_slide_name(file_path)
        save_path = os.path.join(
            CONFIG["path"]["save"],
            slide_name,
            str(CONFIG["patch"]["size"]),
        )
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        ts = large_image.getTileSource(file_path)
        ts_metadata = ts.getMetadata()
        slide_size = ts_metadata.get("sizeX"), ts_metadata.get("sizeY")
        filtered_index = self.get_filtered_index(ts)
        total = len(filtered_index)
        point_index = [int(total * (i / 10)) for i in range(1, 11)]

        # for i, (idx, score) in enumerate(filtered_index):
        for i, idx in enumerate(filtered_index):
            tile_info = ts.getSingleTile(
                scale=dict(magnification=ts_metadata.get("magnification")),
                tile_size=dict(width=self.size, height=self.size),
                tile_position=idx,
            )
            coordinate = (tile_info["x"], tile_info["y"])
            position = tuple([round(x / y, 5) for x, y in zip(coordinate, slide_size)])
            tile_image = tile_info["tile"]
            tile_image = Image.fromarray(tile_image)
            img = tile_image.resize((512, 512))

            tile_name = f"{slide_name}_{idx}_{position}.png"
            tile_save_path = os.path.join(save_path, tile_name)
            img.save(tile_save_path)

            if i in point_index:
                percentage = (point_index.index(i) + 1) * 10
                LOGGER.info(f"{slide_name} - {percentage}% finished")

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
