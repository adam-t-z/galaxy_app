def transform(self, x, y):
    """
    Apply perspective transformation to coordinates.
    """
    # Linear perspective scaling for y-coordinate
    lin_y = y * self.perspective_point_y / self.height
    lin_y = min(lin_y, self.perspective_point_y)  # Cap at the perspective point
    

    # Calculate differences for perspective scaling
    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y
    factor = (diff_y / self.perspective_point_y) ** 4 if diff_y else 0  # Exponential scaling for depth effect

    # Return transformed coordinates
    return int(self.perspective_point_x + diff_x * factor), int(self.perspective_point_y - self.perspective_point_y * factor)
