import cv2
import time
import os
import psutil
import logging
import argparse

# Set up logging
logging.basicConfig(filename='rtsp_recording.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

parser = argparse.ArgumentParser(description='Record RTSP stream to video.')
parser.add_argument('rtsp_url', type=str, help='RTSP stream URL')
parser.add_argument('--output',
                    type=str,
                    default='recordings',
                    help='Output folder for recordings')
parser.add_argument('--duration',
                    type=int,
                    default=0,
                    help='Duration of recording in seconds (0 for unlimited)')
args = parser.parse_args()
rtsp_url = args.rtsp_url
output_folder = args.output
total_duration = args.duration


def print_disk_space():
	disk = psutil.disk_usage('/')
	free_gb = disk.free / (1024 * 1024 * 1024)  # Convert bytes to GB
	percent_free = 100 - disk.percent
	print(f"Available disk space: {percent_free:.2f}% ({free_gb:.2f} GB)")
	logging.info(f"Available disk space: {percent_free:.2f}% ({free_gb:.2f} GB)")


# Print disk space at the start
print_disk_space()

os.makedirs(output_folder, exist_ok=True)
segment_duration = 3600  # 1 hour per file
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 30.0
frame_size = (1280, 720)

# Create VideoCapture object
cap = cv2.VideoCapture(rtsp_url)


def create_video_writer():
	timestamp = time.strftime("%Y%m%d-%H%M%S")
	filename = f"{output_folder}/segment_{timestamp}.mp4"
	return cv2.VideoWriter(filename, fourcc, fps, frame_size)


out = create_video_writer()
segment_start_time = time.time()
total_start_time = time.time()


def check_disk_space():
	disk = psutil.disk_usage('/')
	return disk.percent < 95  # Stop if less than 5% space left


try:
	while True:
		if not check_disk_space():
			logging.warning("Low disk space. Stopping recording.")
			break

		if total_duration > 0 and time.time() - total_start_time > total_duration:
			logging.info(
			    f"Reached specified duration of {total_duration} seconds. Stopping recording."
			)
			break

		ret, frame = cap.read()
		if not ret:
			logging.error("Failed to receive frame. Attempting to reconnect...")
			cap.release()
			time.sleep(5)
			cap = cv2.VideoCapture(rtsp_url)
			continue

		frame = cv2.resize(frame, frame_size)
		out.write(frame)

		# Start a new segment every hour
		if time.time() - segment_start_time > segment_duration:
			out.release()
			out = create_video_writer()
			segment_start_time = time.time()
			logging.info("Started new video segment")

except KeyboardInterrupt:
	logging.info("Recording interrupted by user")
except Exception as e:
	logging.error(f"An error occurred: {str(e)}")
finally:
	cap.release()
	out.release()
	cv2.destroyAllWindows()
	logging.info("Recording finished")

print("Recording complete. Check the log file for details.")
