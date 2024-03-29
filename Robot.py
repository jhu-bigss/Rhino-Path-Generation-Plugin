#import math

class Robot():
    def __init__(self):
        self.joint_x = 0
        self.joint_y = 0
        self.joint_z = 0
        # self.joint_b = 0
        # self.joint_c = 0
        
        self.home_to_rotary_base_x = -108
        self.home_to_rotary_base_y = 175
        self.home_to_rotary_base_z = -278
        self.rotary_base_to_center = 80

        self.home_to_rotary_center_x = self.home_to_rotary_base_x
        self.home_to_rotary_center_y = self.home_to_rotary_base_y
        self.home_to_rotary_center_z = self.home_to_rotary_base_z + self.rotary_base_to_center
        
        self.rotary_center_to_work_origin = 150
        self.offset_focal = 25
        
        self.offset_head_to_sensor_x = 18
        self.offset_head_to_sensor_y = 0
        self.offset_head_to_sensor_z = -2


    def forwardKinematics(self, joints, trivial = False):
        if trivial is True:
            self.pose_laser_x = 0
            self.pose_laser_y = 0
            self.pose_laser_z = 0
            
    def inverseKinematics(self, pt_work_coordinate):
        joint_x = pt_work_coordinate[0] + self.home_to_rotary_center_x
        joint_y = pt_work_coordinate[1] + self.home_to_rotary_center_y
        joint_z = pt_work_coordinate[2] + self.home_to_rotary_center_z + self.rotary_center_to_work_origin + self.offset_focal
        
        return [joint_x, joint_y, joint_z]

    def getWorkPtPosFromSensorJoints(self, data):
        sensor_joint_x = data[0]
        sensor_joint_y = data[1]
        sensor_joint_z = data[2]
        sensor_measured = - data[3]
        
        pt_x = - self.home_to_rotary_center_x + sensor_joint_x + self.offset_head_to_sensor_x
        pt_y = - self.home_to_rotary_center_y + sensor_joint_y + self.offset_head_to_sensor_y
        pt_z = - self.rotary_center_to_work_origin - self.home_to_rotary_center_z  + sensor_joint_z + self.offset_head_to_sensor_z + sensor_measured
        
        return [pt_x, pt_y, pt_z]

if __name__ == "__main__":
    robot = Robot()
    print dir(robot)