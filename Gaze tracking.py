#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:





# In[2]:


import cv2
import numpy as np
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList


# This class estimates the gaze direction based on the head's position.
class HeadPose:
    def __init__(self):
        pass

    def estimate_direction(self, frame: np.array, landmarks: NormalizedLandmarkList, draw_pose_direction: bool = True,
                           angle_threshold: int = 25):
        '''
        :param frame: a frame from the webcam.
        :param landmarks: the NormalizedLandmarkList from Meshpipe.
        :param draw_pose_direction: whether to draw a line from the nose to indicate the pose direction.
        :param angle_threshold: the angle threshold of x and y rotations to determine the direction.
        :return: the annotated frame. The pose direction is annotated in the frame.
        '''

        # Get transformation vectors from world to image
        rot_vector, trans_vector, camera_matrix, dist_coeffs = self.get_world_to_image_trans(frame, landmarks)

        # Draw nose
        if draw_pose_direction:
            # Transform nose end's world point to image point
            nose_end_coor, _ = cv2.projectPoints(np.array([(0.0, 0.0, 500.0)]), rot_vector, trans_vector,
                                                 camera_matrix, dist_coeffs)
            start_nose_coor = self.denorm_coor(landmarks.landmark[4], frame.shape)
            p1 = (int(start_nose_coor[0]), int(start_nose_coor[1]))
            p2 = (int(nose_end_coor[0][0][0]), int(nose_end_coor[0][0][1]))
            frame = cv2.line(frame, p1, p2, (255, 0, 0), 2)

        # Get rotation angles
        x_angle, y_angle, z_angle = self.xyz_rot_angles(rot_vector)

        head_direction = ""
        if y_angle > angle_threshold:
            head_direction = "Left"
        elif y_angle < -angle_threshold:
            head_direction = "Right"
        elif x_angle > angle_threshold:
            head_direction = "Bottom"
        elif x_angle < -angle_threshold:
            head_direction = "Top"
        else:
            head_direction = "Center"

        # Put text regarding pose
        frame = cv2.putText(frame, f"Head x rotation: {x_angle:.0f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 0), 1, 2)
        frame = cv2.putText(frame, f"Head y rotation: {y_angle:.0f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 0), 1, 2)
        frame = cv2.putText(frame, f"Head z rotation: {z_angle:.0f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 0), 1, 2)
        frame = cv2.putText(frame, f"Head pose: {head_direction}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),
                            1, 2)

        return frame

    def xyz_rot_angles(self, rot_vector: np.array):
        '''
        Converts the rotation vector to rotation matrix, and then obtain the angles.
        :param rot_vector: the rotation vector.
        :return: the rotation angles in the x,y,z directions.
        '''
        rot_mat, _ = cv2.Rodrigues(rot_vector)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rot_mat)
        x_angle = angles[0]
        y_angle = angles[1]
        z_angle = angles[2]
        return x_angle, y_angle, z_angle

    def denorm_coor(self, coor, shape):
        '''
        Return the normalized coordinates to the original scale.
        :param coor: x and y coordinates
        :param shape: the frame's dimensions.
        :return: the de-normalized xy coordinates
        '''
        return (int(coor.x * shape[1]), int(coor.y * shape[0]))

    def get_world_to_image_trans(self, frame: np.array, landmarks: NormalizedLandmarkList):
        '''
        Reference: https://learnopencv.com/head-pose-estimation-using-opencv-and-dlib/
        :param frame: a frame from the webcam
        :param landmarks: face landmarks from Meshpipe.
        :return: rotation vector, translation vector, camera intrinsic parameters, distortion coefficients
        '''

        # 2D image coordinates of several facial landmarks
        image_points = np.array([
            self.denorm_coor(landmarks.landmark[4], frame.shape),  # Nose tip
            self.denorm_coor(landmarks.landmark[152], frame.shape),  # Chin
            self.denorm_coor(landmarks.landmark[263], frame.shape),  # Left eye left corner
            self.denorm_coor(landmarks.landmark[33], frame.shape),  # Right eye right corner
            self.denorm_coor(landmarks.landmark[287], frame.shape),  # Left Mouth corner
            self.denorm_coor(landmarks.landmark[57], frame.shape)  # Right mouth corner
        ], dtype="double")

        # 3D World coordinates based on a generic face model
        world_points = np.array([
            (0.0, 0.0, 0.0),  # Nose tip
            (0.0, -330.0, -65.0),  # Chin
            (-225.0, 170.0, -135.0),  # Left eye left corner
            (225.0, 170.0, -135.0),  # Right eye right corner
            (-150.0, -150.0, -125.0),  # Left Mouth corner
            (150.0, -150.0, -125.0)  # Right mouth corner
        ])

        # Estimated camera attributes
        focal_length = frame.shape[1]
        center = (frame.shape[1] / 2, frame.shape[0] / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )

        dist_coeffs = np.zeros((4, 1))  # assuming no lens distortion

        # Get rotation and traslation vectors
        (success, rot_vector, trans_vector) = cv2.solvePnP(world_points, image_points, camera_matrix,
                                                           dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

        return rot_vector, trans_vector, camera_matrix, dist_coeffs


# In[3]:


import numpy as np
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
import cv2


# This class estimates the gaze direction based on the irises' position.
class IrisPose:
    def __init__(self):
        pass

    def estimate_direction(self, frame: np.array, landmarks: NormalizedLandmarkList, draw_pose_direction: bool = True,
                           distance_threshold: int = 2):
        '''
            :param frame: a frame from the webcam.
            :param landmarks: the NormalizedLandmarkList from Meshpipe.
            :param draw_pose_direction: whether to draw a line from the nose to indicate the pose direction.
            :param distance_threshold: the x and y distance threshold for determining the gaze direction.
        '''

        # Iris positions
        left_iris_image_coor = self.get_average_coors(landmarks, (474, 475, 476, 477), frame.shape)
        right_iris_image_coor = self.get_average_coors(landmarks, (468, 469, 470, 471, 472), frame.shape)

        # Center point of both irises
        between_iris_image_coor = ((left_iris_image_coor[0] + right_iris_image_coor[0]) // 2,
                                   (left_iris_image_coor[1] + right_iris_image_coor[1]) // 2)

        # Eye center positions
        left_eye_center_coor = self.get_average_coors(landmarks, (
        263, 249, 390, 373, 374, 380, 381, 382, 362, 263, 466, 388, 387, 386, 385, 384, 398), frame.shape)
        right_eye_center_coor = self.get_average_coors(landmarks, (
        33, 7, 163, 144, 145, 153, 154, 155, 133, 33, 246, 161, 160, 159, 158, 157, 173, 133), frame.shape)

        # Center point of both eyes' center
        between_eyes_image_coor = ((left_eye_center_coor[0] + right_eye_center_coor[0]) // 2,
                                   (left_eye_center_coor[1] + right_eye_center_coor[1]) // 2)

        distance_between_iris_eyes_center = np.array(between_eyes_image_coor) - np.array(between_iris_image_coor)
        x_distance = distance_between_iris_eyes_center[0]
        y_distance = distance_between_iris_eyes_center[1]

        # Get direction
        gaze_direction = ""
        if y_distance >= distance_threshold:
            gaze_direction = "Top"
        elif y_distance < -distance_threshold:
            gaze_direction = "Bottom"
        elif x_distance > distance_threshold:
            gaze_direction = "Left"
        elif x_distance < -distance_threshold:
            gaze_direction = "Right"
        else:
            gaze_direction = "Center"

        # Annotate
        frame = cv2.line(frame, left_iris_image_coor, left_iris_image_coor, (0, 0, 255), 3)
        frame = cv2.line(frame, right_iris_image_coor, right_iris_image_coor, (0, 0, 255), 3)
        frame = cv2.line(frame, between_eyes_image_coor, between_eyes_image_coor, (255, 0, 0), 3)
        frame = cv2.line(frame, between_iris_image_coor, between_iris_image_coor, (0, 0, 255), 3)
        frame = cv2.putText(frame, f"X distance center of eyes and irises: {x_distance}", (10, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 2)
        frame = cv2.putText(frame, f"Y distance center of eyes and irises: {y_distance}", (10, 170),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 2)
        frame = cv2.putText(frame, f"Iris gaze direction: {gaze_direction}", (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 0), 1, 2)

        return frame

    def get_average_coors(self, landmarks, landmark_idxs, shape):
        '''
        Calculate the average of multiple image coordinates.
        :param landmarks: the meshpipe's face landmarks.
        :param landmark_idxs: the indices.
        :param shape: the frame dimensions
        :return:
        '''
        total_x = []
        total_y = []
        for idx in landmark_idxs:
            coor = self.denorm_coor(landmarks.landmark[idx], shape)
            total_x.append(coor[0])
            total_y.append(coor[1])

        avg_x = int(np.mean(total_x))
        avg_y = int(np.mean(total_y))
        return (avg_x, avg_y)

    def denorm_coor(self, coor, shape):
        '''
        Return the normalized coordinates to the original scale.
        :param coor: x and y coordinates
        :param shape: the frame's dimensions.
        :return: the de-normalized xy coordinates
        '''
        return (int(coor.x * shape[1]), int(coor.y * shape[0]))


# In[5]:


import cv2
import mediapipe as mp
import numpy as np



class GazeEstimation():
    def get_face_landmarks(self, frame: np.array, face_mesh: mp.solutions.face_mesh.FaceMesh):
        ''' Returns the meshpipe's face landmarks. This function assumes one face only in a given frame.
        :param image: a frame (in BGR format) captured from the webcam
        :param face_mesh: a Meshpipe's face mesh object
        :return: face landmarks
        '''
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame)

        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]
        else:
            return None

    def webcam_live_gaze_estimation(self, video_device_id: int = 0, draw_meshes: bool = False):
        ''' Capture frames from the video device and performs gaze estimation in real-time.
        :param video_device_id: the id of video device. Set ID = 0 for the in-built webcam.
        :param draw_meshes: whether to overlay the meshes on the face or not.
        '''
        face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True,
                                                    min_detection_confidence=0.5,
                                                    min_tracking_confidence=0.5)
        head_pose = HeadPose()
        iris_pose = IrisPose()

        # Live capture from the camera
        cap = cv2.VideoCapture(video_device_id)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)  # flip for selfie view

            # Obtain face landmarks
            landmarks = self.get_face_landmarks(frame, face_mesh)

            # Draw meshes
            if draw_meshes:
                # Draw face mesh
                mp.solutions.drawing_utils.draw_landmarks(
                    image=frame,
                    landmark_list=landmarks,
                    connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp.solutions.drawing_styles
                    .get_default_face_mesh_tesselation_style())

                # Draw face border, eyebrows, lips, and eyes
                mp.solutions.drawing_utils.draw_landmarks(
                    image=frame,
                    landmark_list=landmarks,
                    connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp.solutions.drawing_styles
                    .get_default_face_mesh_contours_style())

                # Draw irises
                mp.solutions.drawing_utils.draw_landmarks(
                    image=frame,
                    landmark_list=landmarks,
                    connections=mp.solutions.face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp.solutions.drawing_styles
                    .get_default_face_mesh_iris_connections_style())

            if landmarks is not None:
                # Gaze estimation based on head's position
                frame = head_pose.estimate_direction(frame, landmarks)

                # Gaze estimation based on irises
                frame = iris_pose.estimate_direction(frame, landmarks)

            # Display frame on screen
            cv2.imshow('Live gaze estimation', frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # fixes a bug where the window do not close properly on macOS.


if __name__ == "__main__":
    gaze_estimator = GazeEstimation()
    gaze_estimator.webcam_live_gaze_estimation(draw_meshes=False)


# In[ ]:




