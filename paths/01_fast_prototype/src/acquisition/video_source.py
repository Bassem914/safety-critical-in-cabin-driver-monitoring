from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Optional

import cv2
import numpy as np


@dataclass(frozen=True)
class FramePacket:
    """
    Container for one acquired frame and its source metadata.

    Attributes:
        frame:
            OpenCV image in BGR format.

        frame_index:
            Zero-based frame index within the source.

        timestamp_seconds:
            Timestamp on the source timeline.

        source_name:
            Human-readable source identifier.
    """

    frame: np.ndarray
    frame_index: int
    timestamp_seconds: float
    source_name: str


class VideoSource(ABC):
    """
    Abstract interface for live and recorded video sources.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return a human-readable source identifier."""

    @property
    @abstractmethod
    def fps(self) -> float:
        """Return the nominal source frame rate."""

    @abstractmethod
    def is_opened(self) -> bool:
        """Return whether the underlying source opened successfully."""

    @abstractmethod
    def read(self) -> Optional[FramePacket]:
        """
        Read the next frame.

        Returns:
            A FramePacket when acquisition succeeds.
            None when the source ends or frame acquisition fails.
        """

    @abstractmethod
    def release(self) -> None:
        """Release the underlying video resource."""


class WebcamVideoSource(VideoSource):
    """
    Live webcam input.

    Webcam timestamps use monotonic elapsed time from the beginning
    of the acquisition session.
    """

    def __init__(self, camera_index: int = 0) -> None:
        self._camera_index = camera_index
        self._capture = cv2.VideoCapture(camera_index)
        self._frame_index = 0
        self._start_time = perf_counter()

    @property
    def source_name(self) -> str:
        return f"webcam:{self._camera_index}"

    @property
    def fps(self) -> float:
        reported_fps = float(
            self._capture.get(cv2.CAP_PROP_FPS)
        )

        return reported_fps if reported_fps > 0.0 else 0.0

    def is_opened(self) -> bool:
        return self._capture.isOpened()

    def read(self) -> Optional[FramePacket]:
        success, frame = self._capture.read()

        if not success:
            return None

        packet = FramePacket(
            frame=frame,
            frame_index=self._frame_index,
            timestamp_seconds=perf_counter() - self._start_time,
            source_name=self.source_name,
        )

        self._frame_index += 1
        return packet

    def release(self) -> None:
        self._capture.release()


class FileVideoSource(VideoSource):
    """
    Local video-file input.

    Video timestamps are read from the source timeline using
    CAP_PROP_POS_MSEC. When unavailable, frame_index / FPS is used.
    """

    def __init__(self, video_path: str) -> None:
        self._video_path = Path(
            video_path
        ).expanduser().resolve()

        self._capture = cv2.VideoCapture(
            str(self._video_path)
        )

        self._frame_index = 0

        reported_fps = float(
            self._capture.get(cv2.CAP_PROP_FPS)
        )

        self._fps = (
            reported_fps
            if reported_fps > 0.0
            else 0.0
        )

    @property
    def source_name(self) -> str:
        return str(self._video_path)

    @property
    def fps(self) -> float:
        return self._fps

    def is_opened(self) -> bool:
        return self._capture.isOpened()

    def read(self) -> Optional[FramePacket]:
        success, frame = self._capture.read()

        if not success:
            return None

        timestamp_ms = float(
            self._capture.get(cv2.CAP_PROP_POS_MSEC)
        )

        if timestamp_ms > 0.0:
            timestamp_seconds = timestamp_ms / 1000.0
        elif self._fps > 0.0:
            timestamp_seconds = (
                self._frame_index / self._fps
            )
        else:
            timestamp_seconds = 0.0

        packet = FramePacket(
            frame=frame,
            frame_index=self._frame_index,
            timestamp_seconds=timestamp_seconds,
            source_name=self.source_name,
        )

        self._frame_index += 1
        return packet

    def release(self) -> None:
        self._capture.release()