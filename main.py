#! /usr/bin/python3

from pyray import *
import math

WIDTH = 800
HEIGHT = 600

ROBOT_DISPLAY_FONT_SIZE = 20

ROBOT_WIDTH = 100
ROBOT_HEIGHT = 100

ROBOT_START_x = 100
ROBOT_START_y = 100

ROBOT_TURN_POWER = 0.05
ROBOT_SPEED = 0.1
ROBOT_SWERVE_SPEED = 0.1

BIG_CIRCLE_SIZE = 0.10

ZERO_SWERVE_BUTTON = 8

class Robot:

    def __init__(self):
        self.x = ROBOT_START_x
        self.y = ROBOT_START_y
        self.angle = 0

        self.swerve_angle = 0

        self.turn_power = ROBOT_TURN_POWER
        self.speed = ROBOT_SPEED
        self.swerve_speed = ROBOT_SWERVE_SPEED

        self.gamepad_num = 0

        # For getting speed.
        self.old_x = self.x
        self.old_y = self.y
        self.old_angle = self.angle
        self.old_swerve_angle = self.swerve_angle

        self.width = ROBOT_WIDTH
        self.height = ROBOT_HEIGHT

        self.color = BLACK
        self.front_color = BLUE

        self.corner_positions = ()
        self.box_outline = ()
        self.box_data = ()

    
    def get_center_x(self):
        return self.x + (self.width / 2)


    def get_center_y(self):
        return self.y + (self.height / 2)


    def get_x_speed(self):
        return self.x - self.old_x


    def get_y_speed(self):
        return self.y - self.old_y


    def get_rotate_speed(self):
        return self.angle - self.old_angle


    def get_swerve_rotate_speed(self):
        return self.swerve_angle - self.old_swerve_angle


    # Put this at the start of update. Its for getting speed.
    def update_old_values(self):
        self.old_x = self.x
        self.old_y = self.y
        self.old_angle = self.angle
        self.old_swerve_angle = self.swerve_angle


    def update(self):
        self.update_old_values()

        # Keep angle between 0 and 360.
        self.angle %= 360
        self.swerve_angle %= 360

        # Get input.
        turn_power = get_gamepad_axis_movement(self.gamepad_num, GAMEPAD_AXIS_LEFT_X) * self.turn_power
        forward_speed = get_gamepad_axis_movement(self.gamepad_num, GAMEPAD_AXIS_LEFT_Y) * self.speed
        swerve_speed = get_gamepad_axis_movement(self.gamepad_num, GAMEPAD_AXIS_RIGHT_X) * self.swerve_speed

        # Update swerve angle.
        self.swerve_angle += swerve_speed

        # Zero swerve angle.
        if is_gamepad_button_pressed(self.gamepad_num, ZERO_SWERVE_BUTTON):
            self.swerve_angle = 0

        # Update x, y and angle.
        self.x += forward_speed * math.cos(math.radians(self.angle + self.swerve_angle))
        self.y += forward_speed * math.sin(math.radians(self.angle + self.swerve_angle))
        self.angle += (turn_power * forward_speed) + turn_power

        self.update_box_data()


    def update_box_data(self):
        # Get sin and cos values of angle.
        angle_cos = math.cos(math.radians(self.angle))
        angle_sin = math.sin(math.radians(self.angle))

        # Get center of robot.
        center_x = self.get_center_x()
        center_y = self.get_center_y()

        # Get points on robot.
        front_right_x = self.x + self.width
        front_right_y = self.y

        front_left_x = self.x
        front_left_y = self.y

        back_right_x = self.x + self.width
        back_right_y = self.y + self.height

        back_left_x = self.x
        back_left_y = self.y + self.height

        old_front_right_x = front_right_x
        old_front_left_x = front_left_x
        old_back_right_x = back_right_x
        old_back_left_x = back_left_x

        # Rotate points.
        front_right_x = ((front_right_x - center_x) * angle_cos - (front_right_y - center_y) * angle_sin) + center_x
        front_left_x = ((front_left_x - center_x) * angle_cos - (front_left_y - center_y) * angle_sin) + center_x

        back_right_x = ((back_right_x - center_x) * angle_cos - (back_right_y - center_y) * angle_sin) + center_x
        back_left_x = ((back_left_x - center_x) * angle_cos - (back_left_y - center_y) * angle_sin) + center_x

        front_right_y = ((old_front_right_x - center_x) * angle_sin + (front_right_y - center_y) * angle_cos) + center_y
        front_left_y = ((old_front_left_x - center_x) * angle_sin + (front_left_y - center_y) * angle_cos) + center_y

        back_right_y = ((old_back_right_x - center_x) * angle_sin + (back_right_y - center_y) * angle_cos) + center_y
        back_left_y = ((old_back_left_x - center_x) * angle_sin + (back_left_y - center_y) * angle_cos) + center_y
        
        # Set 'corner_positions'.
        self.corner_positions = (
            (front_right_x, front_right_y),
            (front_left_x, front_left_y),
            (back_right_x, back_right_y),
            (back_left_x, back_left_y)
        )

        # Set 'box_outline'.
        self.box_outline = (
            (Vector2(front_left_x, front_left_y), Vector2(back_left_x, back_left_y)),
            (Vector2(front_right_x, front_right_y), Vector2(back_right_x, back_right_y)),
            (Vector2(front_right_x, front_right_y), Vector2(front_left_x, front_left_y)),
            (Vector2(back_right_x, back_right_y), Vector2(back_left_x, back_left_y))
        )

        self.box_data = (self.corner_positions, self.box_outline)
        return self.box_data


    def collided(self, other_robot):

        # Other robot doesn't have a box outline.
        if other_robot.box_outline == ():
            other_robot.update_box_data()

        for line in other_robot.box_outline:
            for line2 in self.box_outline:
                if check_collision_lines(line[0], line[1], line2[0], line2[1], Vector2(0, 0)):
                    return True

        return False


    def draw(self):
        # Get center of robot.
        center_x = self.get_center_x()
        center_y = self.get_center_y()

        # No box outline.
        if self.box_outline == ():
            self.update_box_data()

        # Draw lines.
        draw_line_v(self.box_outline[0][0], self.box_outline[0][1], self.front_color) # Front.

        for i in range(1, 4): # First line already drawn.
            draw_line_v(self.box_outline[i][0], self.box_outline[i][1], self.color)

        circle_rad = (self.width + self.height) * BIG_CIRCLE_SIZE

        # Draw big circle.
        draw_circle(int(center_x), int(center_y), circle_rad, BLACK)

        small_circle_rad = circle_rad / 4 # Small circle is 25% smaller then big circle.

        swerve_angle_cos = math.cos(math.radians(self.swerve_angle + self.angle))
        swerve_angle_sin = math.sin(math.radians(self.swerve_angle + self.angle))

        # Circle postion.
        cx = center_x - circle_rad
        cy = center_y

        old_cx = cx

        # Rotate.
        cx = ((cx - center_x) * swerve_angle_cos - (cy - center_y) * swerve_angle_sin) + center_x
        cy = ((old_cx - center_x) * swerve_angle_sin + (cy - center_y) * swerve_angle_cos) + center_y

        # Draw small circle.
        draw_circle(int(cx), int(cy), small_circle_rad, BLUE)



def main():
    # Open window.
    init_window(WIDTH, HEIGHT, "A tilte that is not needed")

    # Create robot.
    robot = Robot()

    robot2 = Robot()
    robot2.gamepad_num = 1
    robot2.x = 400
    robot2.y = 400
    robot2.angle = 45

    # Draw and update loop.
    while not window_should_close():

        # Update.
        robot.update()
        robot2.update()

        # Draw.
        begin_drawing();

        clear_background(RAYWHITE);

        # Display robot info.
        draw_text(f"X: {robot.x}, Y: {robot.y}, angle: {robot.angle}", 10, 10, ROBOT_DISPLAY_FONT_SIZE, BLACK)

        draw_text(
            f"X Speed: {round(robot.get_x_speed(), 3)}, Y Speed: {round(robot.get_y_speed(), 3)}, Rotate Speed: {robot.get_rotate_speed()}", 
            10, 
            10 + ROBOT_DISPLAY_FONT_SIZE, 
            ROBOT_DISPLAY_FONT_SIZE, 
            BLACK
        )

        draw_text(
            f"Swerve angle: {robot.swerve_angle}, Swerve Speed: {robot.get_swerve_rotate_speed()}", 
            10, 
            10 + (ROBOT_DISPLAY_FONT_SIZE * 2), 
            ROBOT_DISPLAY_FONT_SIZE, 
            BLACK
        )

        draw_text(
            f"Collided: {robot.collided(robot2)}",
            10,
            10 + (ROBOT_DISPLAY_FONT_SIZE * 3),
            ROBOT_DISPLAY_FONT_SIZE,
            BLACK
        )

        # Draw robot.
        robot.draw()
        robot2.draw()

        end_drawing();

    close_window();


if __name__ == "__main__":
    main()
