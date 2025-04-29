import os
import cv2
import numpy as np
import face_recognition
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image
import requests

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = "8013238176:AAFIBhEUUiH8BwBMhi6DG7On_qKj00yCXKc"

# Function to download files from Telegram
def download_file(file_url, file_path):
    response = requests.get(file_url)
    with open(file_path, 'wb') as f:
        f.write(response.content)

# Function to swap faces between image and video
def swap_faces(image_path, video_path, output_path):
    # Load the image
    image = face_recognition.load_image_file(image_path)
    if len(face_recognition.face_encodings(image)) == 0:
        return False, "No face detected in the image."
    image_face_encoding = face_recognition.face_encodings(image)[0]
    image_locations = face_recognition.face_locations(image)[0]

    # Load the video
    video = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        # Convert frame to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces([image_face_encoding], face_encoding)
            if True in matches:
                # Extract the face from the image
                image_face = image[image_locations[0]:image_locations[2], image_locations[3]:image_locations[1]]
                image_face = cv2.resize(image_face, (right - left, bottom - top))

                # Place the image face onto the video frame
                frame[top:bottom, left:right] = cv2.cvtColor(image_face, cv2.COLOR_RGB2BGR)

        if out is None:
            height, width = frame.shape[:2]
            out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))
        out.write(frame)

    video.release()
    out.release()
    return True, "Face swap completed."

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! First send a photo of the face you want to swap, then send a video to swap the face into.")

# Photo handler
def photo_handler(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_path = f"{user.id}_photo.jpg"
    download_file(photo_file.file_path, photo_path)

    # Save the photo path in user data for later use
    context.user_data['photo_path'] = photo_path
    update.message.reply_text("Photo received! Now please send a video to swap the face into.")

# Video handler
def video_handler(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if 'photo_path' not in context.user_data:
        update.message.reply_text("Please send a photo first!")
        return

    video_file = update.message.video.get_file()
    video_path = f"{user.id}_input_video.mp4"
    output_path = f"{user.id}_output.mp4"
    download_file(video_file.file_path, video_path)

    photo_path = context.user_data['photo_path']
    update.message.reply_text("Processing your photo and video... Please wait.")
    
    success, message = swap_faces(photo_path, video_path, output_path)
    if not success:
        update.message.reply_text(message)
    else:
        # Send the result back to the user
        with open(output_path, 'rb') as video:
            update.message.reply_video(video)

    # Clean up
    os.remove(photo_path)
    os.remove(video_path)
    os.remove(output_path)
    context.user_data.pop('photo_path', None)

def main() -> None:
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))
    dispatcher.add_handler(MessageHandler(Filters.video, video_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
